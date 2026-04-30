from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.schemas.users_schemas import UserCreateSchema
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
    

    @staticmethod
    async def change_balance(session: AsyncSession, user_id: int, tokens_change: int) -> Users | None:
        query = (
            update(Users)
            .where(Users.id==user_id)
            .values(current_balance=Users.current_balance+tokens_change)
            .returning(Users)
        )

        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is not None:
            return user
        
        return None