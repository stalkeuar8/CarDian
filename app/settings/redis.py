from typing import AsyncGenerator

import redis.asyncio as async_redis

from app.settings.config import redis_settings

redis_client = async_redis.from_url(redis_settings.REDIS_url, decode_responses=True)


async def get_redis() -> AsyncGenerator[async_redis.Redis, None]:
    try:
        yield redis_client

    finally:
        pass