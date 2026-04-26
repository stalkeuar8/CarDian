from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import contains_eager

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

        if obj is not None:
            return obj
        
        return None
    

    @staticmethod
    async def get_watch_to_check_by_time(earlier_than: datetime, session: AsyncSession) -> Watchlist | None:
        query = (
            select(Watchlist)
            .where(Watchlist.last_time_checked < earlier_than, Watchlist.is_active==True)
            .limit(1)        
            .with_for_update()
        )

        result = await session.execute(query)
        watch = result.scalar_one_or_none()

        if watch is not None:
            return watch
        
        return None


class PriceAlertsRepo(BaseRepo[PriceAlerts]):
    model = PriceAlerts

    @staticmethod
    async def get_by_users_id(session: AsyncSession, current_user_id: int) -> Sequence[PriceAlerts] | None:
        query = (
            select(PriceAlerts)
            .join(PriceAlerts.watchlist)
            .where(Watchlist.user_id==current_user_id)
            .options(contains_eager(PriceAlerts.watchlist))
        )

        results = await session.execute(query)
        alerts = results.scalars().all()

        if alerts:
            return alerts
        
        return None
    

    @staticmethod
    async def get_by_watch_id(session: AsyncSession, current_user_id: int, watchlist_id: int) -> Sequence[PriceAlerts] | None:
        query = (
            select(PriceAlerts)
            .join(PriceAlerts.watchlist)
            .where(Watchlist.user_id==current_user_id, PriceAlerts.watchlist_id==watchlist_id)
            .options(contains_eager(PriceAlerts.watchlist))
        )

        results = await session.execute(query)
        alerts = results.scalars().all()

        if alerts:
            return alerts
        
        return None