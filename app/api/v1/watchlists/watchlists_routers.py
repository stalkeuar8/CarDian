import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Sequence

from app.schemas.watchlists_schemas import WatchlistResponseSchema, WatchlistSequenceResponseSchema, WatchlistRequestSchema, WatchlistCreateSchema
from app.models.watchlists import PriceAlerts, Watchlist
from app.repo.watchlists_repo import WatchlistsRepo, PriceAlertsRepo
from app.models.users import Users
from app.services.price_prediction import predict_service
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user, oauth2_scheme, decode_jwt
from app.utils.password_hasher import get_password_hash
from app.settings.redis import get_redis
from app.background.tasks import process_manual_lookup


watchlists_router = APIRouter(prefix="/v1/watchlists", tags=['Watchlists'])


@watchlists_router.post("/", summary="Add url to watchlist", response_model=WatchlistResponseSchema) 
async def add_to_watchlist(body: WatchlistRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistResponseSchema:
    new_obj_dto = WatchlistCreateSchema(**body.model_dump(), user_id=current_user.id)
    
    new_watchlist: Watchlist | None = await WatchlistsRepo.create(session=session, new_obj_dto=new_obj_dto)

    if not new_watchlist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error while adding url, try later")

    return WatchlistResponseSchema.model_validate(new_watchlist)


@watchlists_router.get("/my", summary="Get user watchlist", response_model=WatchlistSequenceResponseSchema)
async def get_users_watchlist(current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistSequenceResponseSchema:
    watchlist: Sequence[Watchlist] | None = await WatchlistsRepo.find_users_watchlist(current_user_id=current_user.id, session=session, exclude_inactive=True)

    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No watchlist found")

    return WatchlistSequenceResponseSchema(items=[WatchlistResponseSchema.model_validate(item) for item in watchlist], total_items_qty=len(watchlist))


@watchlists_router.get("/my/all", summary="Get user watchlist (including inactive)", response_model=WatchlistSequenceResponseSchema)
async def get_users_watchlist(current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> WatchlistSequenceResponseSchema:
    watchlist: Sequence[Watchlist] | None = await WatchlistsRepo.find_users_watchlist(current_user_id=current_user.id, session=session, exclude_inactive=False)

    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No watchlist found")

    return WatchlistSequenceResponseSchema(items=[WatchlistResponseSchema.model_validate(item) for item in watchlist], total_items_qty=len(watchlist))



@watchlists_router.get("/{watch_id}", summary="Get user watch by id", response_model=WatchlistResponseSchema)
async def get_users_watch_by_id(watch_id: int, session: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)) -> WatchlistResponseSchema:
    watch: Watchlist | None = await WatchlistsRepo.find_by_id(current_user_id=current_user.id, id_to_find=watch_id, session=session)

    if watch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Watch with ID: {watch_id} of this user was not found")
    
    return WatchlistResponseSchema.model_validate(watch)



