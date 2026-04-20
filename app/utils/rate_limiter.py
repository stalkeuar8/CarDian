from fastapi.requests import Request
from functools import wraps
from typing import Callable
from app.settings.redis import get_redis
from redis.asyncio import Redis
from fastapi import HTTPException, status



def rate_limiter(limit: int, window: int):
    def deco(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            key = f"rate_limiter:{request.client.host}:{func.__name__}"
            
            redis_session: Redis = get_redis()

            current_request_num = await redis_session.incr(key)

            if current_request_num and current_request_num > limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests, try a bit later")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return deco