from typing import Any, Generic, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.base import Base

T = TypeVar("T", bound=Base)

class BaseAdminRepo(Generic[T]):

    model: Type[T]

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id_to_get: int, exclude_deleted: bool = False) -> T | None:
        query = (
            select(cls.model).where(cast(Any, cls.model.id)==id_to_get)
        )

        if exclude_deleted:
            query = query.where(cast(Any, cls.model.deleted_at).is_(None))

        result = await session.execute(query)
        obj = result.scalar_one_or_none()

        if obj:
            return obj
        
        return None
    
    