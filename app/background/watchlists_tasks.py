import asyncio
import time
import random
from celery.schedules import crontab
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
from app.background.bot_tasks import send_price_alert_to_bot

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



async def async_watchlist_parsing_processing(self) -> None:
    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    current_time = datetime.now(tz=timezone.utc)
    minimal_time = current_time - timedelta(hours=24)

    watch_to_check = None 
    logger.info("launched")
    async with celery_async_session_factory.begin() as session:
        watch_in_db: Watchlist | None = await WatchlistsRepo.get_watch_to_check_by_time(earlier_than=current_time, session=session)

        if watch_in_db is None:
            return
        
        logger.info(f"get watch: {watch_in_db}")
        watch_to_check = watch_in_db

    watch_id = watch_to_check.id
    last_price = watch_to_check.last_price
    url = watch_to_check.url

    current_price = None
    
    async with CurlAsyncSession() as session:

        response = await session.get(
            url=url,
            impersonate=get_browser(),
            timeout=20
        )

    if response.status_code == 403:
        logger.error(f"GOT 403, URL: {url}")
        return self.retry(countdown=5000)
    
    elif response.status_code in (200, 404):

        async with celery_async_session_factory.begin() as session:
            watch: Watchlist | None = await session.get(Watchlist, watch_id, with_for_update=True)

            if watch is None:
                return
                
            if response.status_code == 200:
                cleaned_json: dict | None = await parse_service.extract_car_data(parsed_html=response.text)
                
                if cleaned_json is None:
                    raise ValueError("Can not extract data from page")

                current_price = cleaned_json['offers'].get("price", None)

                if current_price is None:
                    raise ValueError("Price was not found")
                
                if current_price != last_price:
                    watch.last_price = current_price
                    price_diff = current_price-last_price
                    percents = round(((current_price - last_price) / last_price) * 100, 2)
                
                    price_alert = PriceAlerts(
                        watchlist_id=watch_id,
                        price_diff=price_diff,
                        price_diff_percents=percents,
                        is_sent=False
                    )

                    session.add(price_alert)
                    await session.flush()

                    send_price_alert_to_bot.delay(price_alert.id)

                watch.last_time_checked = current_time        

            if response.status_code == 404:
                watch.is_active = False
                watch.last_time_checked = current_time
        
    else:
        logger.error(f"STATUS CODE {response.status_code}, url: {url}")
        

@celery_app.task(name="watchlist_parsing_procesing", bind=True, max_retries=3)
def watchlist_parsing_procesing(self) -> None:
    time.sleep(random.randint(1, 15))
    return asyncio.run(async_watchlist_parsing_processing(self=self))


celery_app.conf.beat_schedule = {
    "bg_watchlist" : {"task": "watchlist_parsing_procesing", "schedule" : crontab(minute="*")}
}