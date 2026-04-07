from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users_schemas import UserRegisterRequestSchema, UserResponseSchema, UserCreateSchema
from app.settings.database import get_db
from app.models.users import Users
from app.repo.users_repo import UsersRepo
from app.utils.password_hasher import get_password_hash


auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post("/register", summary="Register as user", response_model=UserResponseSchema)
async def register(body: UserRegisterRequestSchema, session: AsyncSession = Depends(get_db)) -> UserResponseSchema | None:
    hashed_password = get_password_hash(body.password)

    new_dto = UserCreateSchema(**body.model_dump(), hashed_password=hashed_password)
    new_user: Users | None = await UsersRepo.create(session=session, new_obj_dto=new_dto)

    if new_user:

        jwt_token = create_access_token(user_id=new_user.id)