from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users_schemas import UserResponseSchema, UserCreateSchema
from app.schemas.auth_schemas import UserAuthResponseSchema, UserLoginRequestSchema, UserRegisterRequestSchema
from app.settings.database import get_db
from app.models.users import Users
from app.repo.users_repo import UsersRepo
from app.utils.password_hasher import get_password_hash
from app.auth.jwt_token import create_access_token, decode_jwt

auth_router = APIRouter(prefix='/v1/auth', tags=['Auth'])


@auth_router.post("/register", summary="Register as user", response_model=UserAuthResponseSchema)
async def register(body: UserRegisterRequestSchema, session: AsyncSession = Depends(get_db)) -> UserAuthResponseSchema | None:
    hashed_password = get_password_hash(body.password)

    new_dto = UserCreateSchema(**body.model_dump(), hashed_password=hashed_password)
    new_user: Users | None = await UsersRepo.create(session=session, new_obj_dto=new_dto)

    if new_user:

        jwt_token = create_access_token(user_id=new_user.id)

        return UserAuthResponseSchema(
            id=new_user.id,
            full_name=new_user.full_name,
            email=new_user.email,
            role=new_user.role,
            created_at=new_user.created_at,
            jwt_token=jwt_token
        )

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can not register you now")
    

@auth_router.post("/login", summary="Login as registered user", response_model=UserAuthResponseSchema)
async def login(body: UserLoginRequestSchema, session: AsyncSession = Depends(get_db)) -> UserAuthResponseSchema | None:
    pass
