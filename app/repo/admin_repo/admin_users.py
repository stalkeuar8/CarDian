from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.users_schemas import UserCreateSchema
from app.schemas.users_schemas import UserResponseSchema
from app.repo.admin_repo.base_admin_repo import BaseAdminRepo
from app.models.users import Users

from datetime import datetime, timezone

class AdminUsersRepo(BaseAdminRepo[Users]):

    model = Users

    @staticmethod
    async def get_by_email(session: AsyncSession, email_to_get: str, exclude_deleted: bool = False) -> Users | None:

        query = select(Users).where(Users.email==email_to_get).with_for_update()
        
        if exclude_deleted:
            query = query.where(Users.deleted_at.is_(None))

        result = await session.execute(query)
        obj = result.scalar_one_or_none()

        if obj: 
            return obj
        
        return None
    

    @staticmethod
    async def change_email(session: AsyncSession, user_id: int, new_email: str) -> Users | None:
        query = (
            update(Users)
            .where(Users.id==user_id, Users.deleted_at.is_(None))
            .values(email=new_email)
            .returning(Users)
        )

        result = await session.execute(query)
        updated_obj = result.scalar_one_or_none()

        if updated_obj:
            return updated_obj
        
        return None
    

    @staticmethod
    async def change_full_name(session: AsyncSession, user_id: int, new_name: str) -> Users | None:
        query = (
            update(Users)
            .where(Users.id==user_id, Users.deleted_at.is_(None))
            .values(full_name=new_name)
            .returning(Users)
        )

        result = await session.execute(query)
        updated_obj = result.scalar_one_or_none()

        if updated_obj:
            return updated_obj
        
        return None
    

    @staticmethod
    async def change_password(session: AsyncSession, user_id: int, new_password: str) -> Users | None:
        query = (
            update(Users)
            .where(Users.id==user_id)
            .values(hashed_password=new_password)
            .returning(Users)
        )

        result = await session.execute(query)
        updated_obj = result.scalar_one_or_none()

        if updated_obj:
            return updated_obj
        
        return None
    

    @staticmethod
    async def soft_delete_user(session: AsyncSession, user_id: int) -> Users | None:
        current_time = datetime.now(tz=timezone.utc)

        query = (
            update(Users)
            .where(Users.id==user_id, Users.deleted_at.is_(None))
            .values(deleted_at=current_time)
            .returning(Users)
        )

        result = await session.execute(query)
        deleted_obj = result.scalar_one_or_none()

        if deleted_obj:
            return deleted_obj
        
        return None
    

    @staticmethod
    async def recover_account(session: AsyncSession, new_user_info: UserCreateSchema) -> Users | None:
        query = (
            update(Users)
            .where(Users.email==new_user_info.email, Users.deleted_at.is_not(None))
            .values(
                email=new_user_info.email, 
                full_name=new_user_info.full_name,
                hashed_password=new_user_info.hashed_password,
                deleted_at=None
            )
            .returning(Users)
        )

        result = await session.execute(query)
        recovered_obj = result.scalar_one_or_none()

        if recovered_obj:
            return recovered_obj
        
        return None