import bcrypt
from redis.asyncio import Redis
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.requests import Request

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.users_schemas import UserCreateSchema
from app.schemas.auth_schemas import TokenType, UserAuthResponseSchema, UserLoginRequestSchema, UserRegisterRequestSchema, UserLogoutResponseSchema, UserRefreshRequestSchema, UserRefreshResponseSchema
from app.settings.database import get_db
from app.models.users import Users
from app.repo.users_repo import UsersRepo
from app.repo.admin_repo.admin_users import AdminUsersRepo
from app.utils.password_hasher import get_password_hash
from app.auth.jwt_token import create_token, decode_jwt, get_current_user, oauth2_scheme
from app.settings.redis import get_redis
from app.settings.config import jwt_settings
from app.utils.rate_limiter import rate_limiter

auth_router = APIRouter(prefix='/v1/auth', tags=['Auth'])

@auth_router.post("/register", summary="Register as user", response_model=UserAuthResponseSchema)
@rate_limiter.limit("3/15 seconds")
async def register(request: Request, body: UserRegisterRequestSchema, session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> UserAuthResponseSchema | None:
    hashed_password = get_password_hash(body.password)

    new_dto = UserCreateSchema(**body.model_dump(), hashed_password=hashed_password)

    user_in_db: Users | None = await AdminUsersRepo.get_by_email(session=session, email_to_get=body.email)

    if user_in_db is not None and user_in_db.deleted_at is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with such email already exists")
    
    elif user_in_db is not None and user_in_db.deleted_at is not None:
        new_user: Users | None = await AdminUsersRepo.recover_account(session=session, new_user_info=new_dto)

    elif user_in_db is None: 
        new_user: Users | None = await UsersRepo.create(session=session, new_obj_dto=new_dto)    

    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can not register you now")

    await session.commit()

    access_token = create_token(user_id=new_user.id, token_type=TokenType.ACCESS)
    refresh_token = create_token(user_id=new_user.id, token_type=TokenType.REFRESH)

    refresh_jti = decode_jwt(refresh_token).get("jti")

    await redis.set(f"refresh:{new_user.id}", refresh_jti, ex=jwt_settings.REF_EXP_TIME*60)

    return UserAuthResponseSchema(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        role=new_user.role,
        created_at=new_user.created_at,
        access_token=access_token,
        refresh_token=refresh_token
    )

    

@auth_router.post("/login", summary="Login as registered user", response_model=UserAuthResponseSchema)
@rate_limiter.limit("3/15 seconds")
async def login(request: Request, body: UserLoginRequestSchema, session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> UserAuthResponseSchema:
    user: Users | None = await AdminUsersRepo.get_by_email(session=session, email_to_get=body.email, exclude_deleted=True)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User with such email is not registered")
    
    if not bcrypt.checkpw(body.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")

    access_token = create_token(user_id=user.id, token_type=TokenType.ACCESS)
    refresh_token = create_token(user_id=user.id, token_type=TokenType.REFRESH)
    
    refresh_jti = decode_jwt(refresh_token).get("jti")

    await redis.set(f"refresh:{user.id}", refresh_jti, ex=jwt_settings.REF_EXP_TIME*60)

    return UserAuthResponseSchema(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        access_token=access_token,
        refresh_token=refresh_token
    )


@auth_router.post("/logout", summary="Logout", response_model=UserLogoutResponseSchema)
@rate_limiter.limit("3/15 seconds")
async def logout(request: Request, jwt_token: str = Depends(oauth2_scheme), redis: Redis = Depends(get_redis)) -> UserLogoutResponseSchema:
    
    payload = decode_jwt(jwt_token=jwt_token)

    jti = payload.get("jti", None)
    
    if jti is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, JTI was not found") 

    is_in_blacklist = await redis.get(f"blacklist:{jti}")

    if is_in_blacklist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This token is already logged out") 
    
    user_id = payload.get("sub", None)

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, SUB was not found") 
    
    exp = payload.get("exp", None)

    if exp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, EXP was not found") 
    
    current_time_seconds = int(datetime.now(tz=timezone.utc).timestamp())
    time_left = exp - current_time_seconds

    if time_left > 0:
        await redis.set(f"blacklist:{jti}", "1", ex=time_left)
        await redis.delete(f"refresh:{user_id}")
        
        
    return UserLogoutResponseSchema(status=status.HTTP_200_OK, is_logged_out=True, message="Logged out successfully.")



@auth_router.post("/refresh", summary="Refresh access token", response_model=UserRefreshResponseSchema)
@rate_limiter.limit("3/15 seconds")
async def refresh(request: Request, body: UserRefreshRequestSchema, redis: Redis = Depends(get_redis)) -> UserRefreshResponseSchema:

    payload = decode_jwt(body.refresh_token)

    token_type = payload.get("type", None)

    if token_type is None or token_type != TokenType.REFRESH.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti", None)
    user_id = payload.get("sub", None)

    if jti is None or user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    jti_from_redis = await redis.get(f"refresh:{user_id}")

    if not jti_from_redis: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please, login one more time")

    if jti_from_redis != jti:
        await redis.delete(f"refresh:{user_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong refresh token, login one more time")
    
    new_access = create_token(user_id=user_id, token_type=TokenType.ACCESS)
    new_refresh = create_token(user_id=user_id, token_type=TokenType.REFRESH)

    new_refresh_jti = decode_jwt(new_refresh).get("jti")

    await redis.set(f"refresh:{user_id}", new_refresh_jti, ex=jwt_settings.REF_EXP_TIME*60)

    return UserRefreshResponseSchema(access_token=new_access, refresh_token=new_refresh)
    
