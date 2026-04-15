from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.users_schemas import UserCreateSchema
from app.schemas.users_schemas import UserResponseSchema
from app.repo.admin_repo.base_admin_repo import BaseAdminRepo
from app.models.watchlists import Watchlist, PriceAlerts

from datetime import datetime, timezone

class AdminWatchlistsRepo(BaseAdminRepo[Watchlist]):

    model = Watchlist

    @staticmethod
    async def deactivate_users_watchlists(session: AsyncSession, user_id: int) -> Sequence[Watchlist] | None:

        query = (
            update(Watchlist)
            .where(Watchlist.user_id==user_id)
            .values(is_active=False)
            .returning(Watchlist)
        )

        results = await session.execute(query)
        deleted_watchlists = results.scalars().all()

        if deleted_watchlists:
            return deleted_watchlists
        
        return None
    

class AdminAlertsRepo(BaseAdminRepo[PriceAlerts]):

    model = PriceAlerts
