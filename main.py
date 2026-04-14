from fastapi import FastAPI

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from app.settings.database import async_engine
from app.api.v1.users.users_routers import users_router
from app.api.v1.auth.auth_routers import auth_router
from app.api.v1.lookups.lookups_routers import lookups_routers

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    yield
    await async_engine.dispose()


def create_app() -> FastAPI:
     
    app = FastAPI(title="CarDian", lifespan=lifespan)
    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(lookups_routers)
    return app


app = create_app()
