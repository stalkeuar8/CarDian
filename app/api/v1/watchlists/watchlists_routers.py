from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.watchlists_schemas import WatchlistResponseSchema, WatchlistSequenceResponseSchema, WatchlistRequestSchema, WatchlistCreateSchema
from app.schemas.price_alerts_schemas import PriceAlertResponseSchema, PriceAlertSequenceResponseSchema
from app.models.watchlists import PriceAlerts, Watchlist
from app.repo.watchlists_repo import WatchlistsRepo, PriceAlertsRepo
from app.models.users import Users
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user
from app.utils.rate_limiter import rate_limiter


watchlists_router = APIRouter(prefix="/api/v1/watchlists", tags=['Watchlists'])
price_alerts_router = APIRouter(prefix="/api/v1/alerts", tags=['Watchlists'])


@watchlists_router.post("/", summary="Add url to watchlist", response_model=WatchlistResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def add_to_watchlist(request: Request, body: WatchlistRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistResponseSchema:
    if current_user.current_balance < 5:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"Not enough tokens to add URL to watchlist")
    
    new_obj_dto = WatchlistCreateSchema(**body.model_dump(), user_id=current_user.id)
    
    new_watchlist: Watchlist | None = await WatchlistsRepo.create(session=session, new_obj_dto=new_obj_dto)

    if not new_watchlist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while adding url, try later")

    current_user.current_balance -= 5

    return WatchlistResponseSchema.model_validate(new_watchlist)


@watchlists_router.get("/my", summary="Get user watchlist", response_model=WatchlistSequenceResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def get_users_watchlist(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistSequenceResponseSchema:
    watchlist: Sequence[Watchlist] | None = await WatchlistsRepo.find_users_watchlist(current_user_id=current_user.id, session=session, exclude_inactive=True)

    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No watchlist found")

    return WatchlistSequenceResponseSchema(items=[WatchlistResponseSchema.model_validate(item) for item in watchlist], total_items_qty=len(watchlist))


@watchlists_router.get("/my/all", summary="Get user watchlist (including inactive)", response_model=WatchlistSequenceResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def get_users_watchlist_including_inactive(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistSequenceResponseSchema:
    watchlist: Sequence[Watchlist] | None = await WatchlistsRepo.find_users_watchlist(current_user_id=current_user.id, session=session, exclude_inactive=False)

    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No watchlist found")

    return WatchlistSequenceResponseSchema(items=[WatchlistResponseSchema.model_validate(item) for item in watchlist], total_items_qty=len(watchlist))



@watchlists_router.get("/{watch_id}", summary="Get user watch by id", response_model=WatchlistResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def get_users_watch_by_id(request: Request, watch_id: int, session: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)) -> WatchlistResponseSchema:
    watch: Watchlist | None = await WatchlistsRepo.find_by_id(current_user_id=current_user.id, id_to_find=watch_id, session=session)

    if watch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Watch with ID: {watch_id} of this user was not found")
    
    return WatchlistResponseSchema.model_validate(watch)


@price_alerts_router.get("/", summary="Get my alerts", response_model=PriceAlertSequenceResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_my_alerts(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> PriceAlertSequenceResponseSchema:
    alerts: Sequence[PriceAlerts] | None = await PriceAlertsRepo.get_by_users_id(session=session, current_user_id=current_user.id)

    if alerts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No alerts were found for user ID: {current_user.id}")
    
    return PriceAlertSequenceResponseSchema(items=[PriceAlertResponseSchema.model_validate(alert) for alert in alerts], total_items_qty=len(alerts))


@price_alerts_router.get("/{watchlist_id}", summary="Get my alerts by watch id", response_model=PriceAlertResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_my_alerts(request: Request, watchlist_id: int, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> PriceAlertResponseSchema:
    alerts: Sequence[PriceAlerts] | None = await PriceAlertsRepo.get_by_watch_id(watchlist_id=watchlist_id, session=session, current_user_id=current_user.id)

    if alerts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No alerts were found for watch ID: {watchlist_id}")
    
    return PriceAlertSequenceResponseSchema(items=[PriceAlertResponseSchema.model_validate(alert) for alert in alerts], total_items_qty=len(alerts))