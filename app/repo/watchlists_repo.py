from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.lookups_schemas import ManualLookupRequestSchema, ParsedLookupUpdatingSchema
from app.models.watchlists import PriceAlerts, Watchlist
from app.repo.base_repo import BaseRepo


class WatchlistsRepo(BaseRepo[Watchlist]):
    model = Watchlist


    @staticmethod
    async def find_users_watchlist(current_user_id: int, session: AsyncSession, exclude_inactive: bool) -> Sequence[Watchlist]:
        query = (
            select(Watchlist).where(Watchlist.user_id==current_user_id)
        )

        if exclude_inactive:
            query = query.where(Watchlist.is_active==True)

        result = await session.execute(query)
        obj = result.scalars().all()

        if obj:
            return obj
        
        return None

class PriceAlertsRepo(BaseRepo[PriceAlerts]):
    model = PriceAlerts