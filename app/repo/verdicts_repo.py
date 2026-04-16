from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verdicts import Verdicts
from app.models.lookups import ManualLookups, ParsedLookups


class VerdictsRepo:

    @staticmethod
    async def get_by_manual_lookup_id(session: AsyncSession, user_id: int, manual_lookup_id: int) -> Verdicts | None:
        query = (
            select(Verdicts)
            .join(ManualLookups, ManualLookups.id==manual_lookup_id)
            .where(Verdicts.manual_lookup_id==manual_lookup_id, ManualLookups.user_id==user_id)
        )

        result = await session.execute(query)
        verdict = result.scalar_one_or_none()

        if verdict:
            return verdict
        
        return None
    

    @staticmethod
    async def get_by_parsed_lookup_id(session: AsyncSession, user_id: int, parsed_lookup_id: int) -> Verdicts | None:
        query = (
            select(Verdicts)
            .join(ParsedLookups, ParsedLookups.id==parsed_lookup_id)
            .where(Verdicts.parsed_lookup_id==parsed_lookup_id, ParsedLookups.user_id==user_id)
        )

        result = await session.execute(query)
        verdict = result.scalar_one_or_none()

        if verdict:
            return verdict
        
        return None