from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verdicts import Verdicts
from app.models.lookups import ManualLookups, ParsedLookups


class BaseVerdictsRepo:

    @classmethod
    async def get_by_manual_lookup_id(cls, session: AsyncSession, manual_lookup_id: int, user_id: int | None = None) -> Verdicts | None:
        query = (
            select(Verdicts)
            .where(Verdicts.manual_lookup_id==manual_lookup_id)
        )

        if user_id is not None:
            query = query.join(ManualLookups, ManualLookups.id==manual_lookup_id).where(ManualLookups.user_id==user_id)

        result = await session.execute(query)
        verdict = result.scalar_one_or_none()

        if verdict:
            return verdict
        
        return None
    
    @classmethod
    async def get_by_parsed_lookup_id(cls, session: AsyncSession, parsed_lookup_id: int, user_id: int | None = None) -> Verdicts | None:
        query = (
            select(Verdicts)
            .where(Verdicts.parsed_lookup_id==parsed_lookup_id)
        )

        if user_id is not None:
            query = query.join(ParsedLookups, ParsedLookups.id==parsed_lookup_id).where(ParsedLookups.user_id==user_id)
        
        result = await session.execute(query)
        verdict = result.scalar_one_or_none()

        if verdict:
            return verdict
        
        return None

class VerdictsRepo(BaseVerdictsRepo):

    @classmethod
    async def get_by_manual_lookup_id(cls, session: AsyncSession, user_id: int, manual_lookup_id: int) -> Verdicts | None:
        return await super().get_by_manual_lookup_id(session=session, user_id=user_id, manual_lookup_id=manual_lookup_id)
    
    
    @classmethod
    async def get_by_parsed_lookup_id(cls, session: AsyncSession, user_id: int, parsed_lookup_id: int) -> Verdicts | None:
        return await super().get_by_parsed_lookup_id(session=session, user_id=user_id, parsed_lookup_id=parsed_lookup_id)
    

class AdminVerdictsRepo(BaseVerdictsRepo):

    @classmethod
    async def admin_get_by_manual_lookup_id(cls, session: AsyncSession, manual_lookup_id: int) -> Verdicts | None:
        return await super().get_by_manual_lookup_id(session=session, manual_lookup_id=manual_lookup_id)
    
    
    @classmethod
    async def admin_get_by_parsed_lookup_id(cls, session: AsyncSession, parsed_lookup_id: int) -> Verdicts | None:
        return await super().get_by_parsed_lookup_id(session=session, parsed_lookup_id=parsed_lookup_id)