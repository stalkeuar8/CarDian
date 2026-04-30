from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.stats_schema import StatsResponseSchema
from app.repo.admin_repo.admin_stats_repo import AdminStatsRepo
from app.models.users import Users
from app.settings.database import get_db
from app.auth.jwt_token import get_current_admin_user
from app.utils.rate_limiter import rate_limiter

admin_stats_router = APIRouter(prefix="/v1/admin/lookups", tags=['Admin (Lookups)'])
 

@admin_stats_router.get("/stats", summary="Get all platform stats", response_model=StatsResponseSchema)
@rate_limiter.limit("100/15 seconds")
async def get_platform_stats(request: Request, get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> StatsResponseSchema:
    stats: StatsResponseSchema | None = await AdminStatsRepo.get_platform_stats(session=session)

    if stats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error, cant get platform stats now")
    
    return stats