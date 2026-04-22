import asyncio
from curl_cffi.requests import AsyncSession as CurlAsyncSession
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.background.celery_worker import celery_app
from app.settings.config import database_settings
from app.models.watchlists import Watchlist, PriceAlerts
from app.repo.watchlists_repo import WatchlistsRepo, PriceAlertsRepo
from app.schemas.watchlists_schemas import WatchlistResponseSchema
from app.schemas.price_alerts_schemas import PriceAlertResponseSchema, PriceAlertRequestSchema
from app.utils.browsers import get_browser
from app.services.parse_service import parse_service

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import logging
import sys

logging.basicConfig(
    level=logging.INFO,  
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def async_process_sending_alert(price_alert_id: int) -> None:
    ...


@celery_app.task(name='send_price_alert_to_bot')
def send_price_alert_to_bot(price_alert_id: int) -> None:
    return asyncio.run(async_process_sending_alert(price_alert_id=price_alert_id))