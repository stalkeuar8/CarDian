from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Sequence

from app.repo.base_repo import BaseRepo
from app.models.users import Payments

class PaymentsRepo(BaseRepo[Payments]):
    model = Payments

    @staticmethod
    async def find_by_user_id(cls, session: AsyncSession, current_user_id: int) -> Sequence[Payments] | None:

        query = (
            select(Payments)
            .where(Payments.user_id==current_user_id)
        )
    
        result = await session.execute(query)
        found_objects = result.scalars().all()

        if found_objects:
            return found_objects
        
        return None