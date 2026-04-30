import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.users_schemas import UserResponseSchema, EmailChangeRequestSchema, FullNameChangeRequestSchema, PasswordChangeRequestSchema, DeleteUserRequestSchema, DeleteUserResponseSchema
from app.repo.admin_repo.admin_users import AdminUsersRepo
from app.models.users import Users
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user, oauth2_scheme, decode_jwt
from app.utils.password_hasher import get_password_hash
from app.settings.redis import get_redis
from app.utils.rate_limiter import rate_limiter

users_router = APIRouter(prefix="/api/v1/users", tags=['Users'])

@users_router.get("/profile", summary="Get current user profile", response_model=UserResponseSchema)
async def get_my_profile(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> Users:
    return UserResponseSchema.model_validate(current_user) 


@users_router.patch("/email", summary="Change user's email", response_model=UserResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def change_user_email(request: Request, body: EmailChangeRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> UserResponseSchema:
    updated_user: Users | None = await AdminUsersRepo.change_email(session=session, user_id=current_user.id, new_email=body.new_email)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    
    return UserResponseSchema.model_validate(updated_user)


@users_router.patch("/fullname", summary="Change user's full name", response_model=UserResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def change_user_name(request: Request, body: FullNameChangeRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> UserResponseSchema:
    updated_user: Users | None = await AdminUsersRepo.change_full_name(session=session, user_id=current_user.id, new_name=body.new_full_name)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    
    return UserResponseSchema.model_validate(updated_user)


@users_router.patch("/password", summary="Change user's password", response_model=UserResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def change_password(request: Request, body: PasswordChangeRequestSchema, jwt_token: str = Depends(oauth2_scheme), current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> UserResponseSchema:

    is_in_blacklist = await redis.get(f"pass_change_blacklist:{current_user.id}")
        
    if is_in_blacklist:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="You are out of attempts to change password, try later.")
    
    if not bcrypt.checkpw(body.old_password.encode("utf-8"), current_user.hashed_password.encode("utf-8")):
        try:

            last_attempt = await redis.get(f"pass_change_attempts:{current_user.id}")
            
            if last_attempt:

                last_attempt = int(last_attempt)
                
                if 0 < last_attempt < 3:
                    current_attempt = last_attempt + 1
                    await redis.set(f"pass_change_attempts:{current_user.id}", str(current_attempt), ex=21600)
                
                else:
                    payload = decode_jwt(jwt_token=jwt_token)
                    jti = payload.get("jti", None)
                    exp = payload.get("exp", None)

                    if jti is None or exp is None:
                        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
                        
                    current_time_seconds = int(datetime.now(tz=timezone.utc).timestamp())
                    time_left = exp - current_time_seconds

                    if time_left > 0:
                        await redis.set(f"blacklist:{jti}", "1", ex=time_left)
                    
                    await redis.delete(
                        f"refresh:{current_user.id}", 
                        f"pass_change_attempts:{current_user.id}"
                    )
                    await redis.set(f"pass_change_blacklist:{current_user.id}", "1", ex=21600)
                    raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="You are out of attempts to change password, try later in 6 hours.")
                    
            else:
                current_attempt = 1
                await redis.set(f"pass_change_attempts:{current_user.id}", str(current_attempt), ex=21600)
            
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Wrong current password, you have {3-current_attempt} more attempts")
        
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)
        except Exception as e:
            raise e
        
    await redis.delete(
        f"refresh:{current_user.id}", 
        f"pass_change_attempts:{current_user.id}"
    )

    new_password_hash = get_password_hash(body.new_password)
  
    updated_user: Users | None = await AdminUsersRepo.change_password(session=session, user_id=current_user.id, new_password=new_password_hash)

    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found") 

    return UserResponseSchema.model_validate(updated_user)


@users_router.delete("/me", summary="Deactivate users profile", response_model=DeleteUserResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def deactivate_profile(request: Request, body: DeleteUserRequestSchema, jwt_token: str = Depends(oauth2_scheme), current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> DeleteUserResponseSchema:
    
    if not bcrypt.checkpw(body.current_password.encode("utf-8"), current_user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")
    
    deleted_user: Users | None = await AdminUsersRepo.soft_delete_user(session=session, user_id=current_user.id)

    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is already deleted or not found")
    
    await redis.delete(f"refresh:{current_user.id}") 
    
    payload = decode_jwt(jwt_token=jwt_token)
    jti = payload.get("jti", None)
    exp = payload.get("exp", None)

    if jti is None or exp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
        
    current_time_seconds = int(datetime.now(tz=timezone.utc).timestamp())
    time_left = exp - current_time_seconds

    if time_left > 0:
        await redis.set(f"blacklist:{jti}", "1", ex=time_left)

    return DeleteUserResponseSchema(is_deleted=True, deleted_at=deleted_user.deleted_at)