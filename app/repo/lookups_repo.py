from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.lookups_schemas import ManualLookupRequestSchema, ParsedLookupUpdatingSchema
from app.models.lookups import ManualLookups, ParsedLookups
from app.repo.base_repo import BaseRepo


class ManualLookupsRepo(BaseRepo[ManualLookups]):
    model = ManualLookups

    @staticmethod 
    async def get_all_users_lookups(user_id: int, session: AsyncSession) -> Sequence[ManualLookups] | None:
        query = (
            select(ManualLookups)
            .where(ManualLookups.user_id==user_id)
        )

        results = await session.execute(query)
        lookups = results.scalars().all()

        if lookups:
            return lookups
        
        return None

class ParsedLookupsRepo(BaseRepo[ParsedLookups]):
    model = ParsedLookups

    @staticmethod 
    async def get_all_users_lookups(user_id: int, session: AsyncSession) -> Sequence[ParsedLookups] | None:
        query = (
            select(ParsedLookups)
            .where(ParsedLookups.user_id==user_id)
        )

        results = await session.execute(query)
        lookups = results.scalars().all()

        if lookups:
            return lookups
        
        return None
    

    @staticmethod
    async def update_after_analyzing(session: AsyncSession, lookup_id: int, updated_info: ParsedLookupUpdatingSchema) -> ParsedLookups | None:
        query = (
            update(ParsedLookups)
            .where(ParsedLookups.id==lookup_id)
            .returning(ParsedLookups)
            .values(
                price_listed=updated_info.price_listed,
                status=updated_info.status,
                **updated_info.car_info.model_dump()
            )
        )

        result = await session.execute(query)
        updated_lookup = result.scalar_one_or_none()

        if updated_info is not None:
            return updated_info
        
        return None

