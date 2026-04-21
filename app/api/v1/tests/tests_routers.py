from fastapi import HTTPException, status, APIRouter
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
from app.background.lookups_processing_tasks import process_manual_lookup
from app.background.watchlists_tasks import watchlist_parsing_procesing

tests_router = APIRouter(prefix='/test', tags=['For test'])

@tests_router.post("/")
async def test_task(session:AsyncSession = Depends(get_db)):
    bg_task = watchlist_parsing_procesing.delay()
    return {"status":"200 OK"}