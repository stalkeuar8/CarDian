from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.users import Users
from app.models.lookups import ParsedLookups, ManualLookups
from app.models.watchlists import PriceAlerts, Watchlist
from app.schemas.stats_schema import StatsResponseSchema


class AdminStatsRepo:

    @staticmethod
    async def get_platform_stats(session: AsyncSession) -> StatsResponseSchema:
        query = select(
            func.count(Users.id),
            func.count(ManualLookups.id),
            func.count(ParsedLookups.id),
            func.count(Watchlist.id),
            func.count(PriceAlerts.id)
        )

        result = await session.execute(query)
        stats = result.tuple().one()

        return StatsResponseSchema(
            total_users=stats[0],
            total_manual_lookups=stats[1],
            total_parsed_lookups=stats[2],
            total_watchlist=stats[3],
            total_price_alerts=stats[4]
        )