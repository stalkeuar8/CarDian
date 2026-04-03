from fastapi import FastAPI

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from app.settings.database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    yield
    await async_engine.dispose()


def create_app() -> FastAPI:
     
    app = FastAPI(title="CarDian", lifespan=lifespan)

    return app


app = create_app()
