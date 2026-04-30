from typing import Any, Generic, Type, TypeVar, cast
from pydantic import BaseModel
from datetime import datetime, timezone


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.base import Base

T = TypeVar("T", bound=Base)

class BaseRepo(Generic[T]):

    model: Type[T]

    @classmethod
    async def create(cls, session: AsyncSession, new_obj_dto: BaseModel) -> T | None:

        new_obj = cls.model(**new_obj_dto.model_dump())

        session.add(new_obj)
        await session.flush()

        if new_obj:
            return new_obj
        
        return None


    # @classmethod
    # async def bulk_create(cls, session: AsyncSession, new_objects_dtos: SequenceBaseSchema) -> Sequence[T] | None:

    #     new_objs = [cls.model(**new_obj_dto.model_dump()) for new_obj_dto in new_objects_dtos.items]

    #     session.add_all(new_objs)
    #     await session.flush()

    #     if new_objs:
    #         return new_objs
        
    #     return None
    

    @classmethod
    async def find_by_id(cls, session: AsyncSession, current_user_id: int, id_to_find: int) -> T | None:

        query = (
            select(cls.model)
            .where(cast(Any, cls.model.id)==id_to_find, cast(Any, cls.model.user_id)==current_user_id)
        )
    
        result = await session.execute(query)
        found_object = result.scalar_one_or_none()

        if found_object:
            return found_object
        
        return None
    

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, current_user_id: int, id_to_delete: int) -> T | None:

        current_time = datetime.now(tz=timezone.utc)
        
        query = (
            update(cls.model)
            .where(cast(Any, cls.model.id)==id_to_delete, cast(Any, cls.model.user_id)==current_user_id)
            .values(deleted_at=current_time)
            .returning(cls.model)
        )

        result = await session.execute(query)
        deleted_object = result.scalar_one_or_none()

        if deleted_object:
            return deleted_object
        
        return None