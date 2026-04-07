from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.users_schemas import UserRegisterRequestSchema, UserResponseSchema
from app.repo.base_repo import BaseRepo
from app.models.users import Users

class UsersRepo(BaseRepo[Users]):

    model = Users

    