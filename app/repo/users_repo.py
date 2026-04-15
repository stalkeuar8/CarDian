from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.users_schemas import UserCreateSchema
from app.repo.base_repo import BaseRepo
from app.models.users import Users

class UsersRepo:

    @staticmethod
    async def create(session: AsyncSession, new_obj_dto: UserCreateSchema) -> Users | None:

        new_obj = Users(**new_obj_dto.model_dump())

        session.add(new_obj)
        await session.flush()

        if new_obj:
            return new_obj
        
        return None