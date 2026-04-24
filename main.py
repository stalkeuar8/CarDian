from fastapi import FastAPI
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from app.settings.database import async_engine
from app.api.v1.users.users_routers import users_router
from app.api.v1.auth.auth_routers import auth_router
from app.api.v1.lookups.manual_lookups_routers import manual_lookups_router
from app.api.v1.lookups.parsed_lookups_routers import parsed_lookups_router
from app.api.v1.watchlists.watchlists_routers import watchlists_router, price_alerts_router
from app.api.v1.tests.tests_routers import tests_router
from app.settings.redis import get_redis
from app.utils.rate_limiter import rate_limiter

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    yield
    await async_engine.dispose()


def create_app() -> FastAPI:
     
    app = FastAPI(title="CarDian", lifespan=lifespan)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(manual_lookups_router)
    app.include_router(parsed_lookups_router)
    app.include_router(watchlists_router)
    app.include_router(price_alerts_router)
    app.include_router(tests_router)

    app.state.limiter = rate_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return app


app = create_app()
