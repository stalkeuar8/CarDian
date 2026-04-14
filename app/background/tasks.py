import asyncio

from app.background.celery_worker import celery_app
from app.models.lookups import ManualLookups
from app.services.price_prediction import predict_service
from app.models.verdicts import Verdicts
from app.schemas.verdicts_schemas import VerdictTypes
from app.schemas.prediction_schemas import BasePredictor
from app.schemas.lookup_enums import ManualLookupsStatus
from app.settings.config import database_settings

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text





async def async_process_manual_lookup(lookup_id: int) -> None:

    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    try:
        lookup = None

        async with celery_async_session_factory.begin() as session:
            lookup_info: ManualLookups | None = await session.get(ManualLookups, lookup_id)
            
            if lookup_info is None:
                raise ValueError(f"Lookup with ID: {lookup_id} was not found")
            
            lookup = lookup_info

            car_info_to_predict = BasePredictor.model_validate(lookup)
        

        predicted_price = predict_service.predict(data_to_predict=car_info_to_predict)
        
        try:
            #gemini logic
            llm_feedback = None
            is_gemini_completed = True
        except Exception as e:
            is_gemini_completed = False

        verdict = Verdicts(
            manual_lookup_id=lookup_id, 
            predicted_price=predicted_price,
            verdict=VerdictTypes.no_type,
            llm_feedback=llm_feedback
        )

        async with celery_async_session_factory.begin() as session:
            session.add(verdict)
            
            lookup: ManualLookups | None = await session.get(ManualLookups, lookup_id)
            if is_gemini_completed:
                lookup.status = ManualLookupsStatus.completed
            else:
                lookup.status = ManualLookupsStatus.gemini_failed

            lookup.price_listed = predicted_price

    finally:
        await celery_async_engine.dispose()


@celery_app.task
def process_manual_lookup(lookup_id: int):
    return asyncio.run(async_process_manual_lookup(lookup_id=lookup_id))