import asyncio

from app.background.celery_worker import celery_app
from app.models.lookups import ManualLookups, ParsedLookups, ParsedLookupsRawData
from app.services.price_prediction import predict_service
from app.models.verdicts import Verdicts
from app.schemas.verdicts_schemas import VerdictTypes
from app.schemas.prediction_schemas import BasePredictor
from app.schemas.lookup_enums import ManualLookupsStatus, ParsedLookupsStatus
from app.schemas.lookups_schemas import CarSchema, ParsedLookupsRequestSchema
from app.schemas.gemini_schemas import GeminiAnalyzeRequestSchema, GeminiAnalyzeResponseSchema, GeminiExtractorRequestSchema, GeminiExtractorResponseSchema
from app.settings.config import database_settings
from app.services.gemini_service import gemini_service

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

import logging
import sys

logging.basicConfig(
    level=logging.INFO,  
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def async_process_manual_lookup(lookup_id: int) -> None:

    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    lookup = None

    try:
        
        async with celery_async_session_factory.begin() as session:
            lookup_info: ManualLookups | None = await session.get(ManualLookups, lookup_id)
            
            if lookup_info is None:
                raise ValueError(f"Manual Lookup with ID: {lookup_id} was not found")
            
            lookup = lookup_info

            car_info = CarSchema.model_validate(lookup)
        
        predicted_price = predict_service.predict(data_to_predict=car_info)

        info_to_analyze = GeminiAnalyzeRequestSchema(**car_info.model_dump(), predicted_price=predicted_price)
        
        try:

            gemini_result: GeminiAnalyzeResponseSchema = await gemini_service.analyze_existing(info_to_analyze)
            
            llm_feedback = gemini_result.response
            is_gemini_completed = True
            
        except Exception as e:
            is_gemini_completed = False
            llm_feedback = None


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
def process_manual_lookup(lookup_id: int) -> None:
    return asyncio.run(async_process_manual_lookup(lookup_id=lookup_id))



async def async_process_parsed_lookup(lookup_id: int) -> None:
    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    parsed_lookup = None

    try:
        async with celery_async_session_factory.begin() as session:
            lookup: ParsedLookups | None = await session.get(ParsedLookups, lookup_id)

            if lookup is None:
                raise ValueError(f"Parsed Lookup with ID: {lookup_id} was not found")

            parsed_lookup = lookup

        parsing_dto = ParsedLookupsRequestSchema(url=parsed_lookup.url)

        parsed_text = ...

        parsed_car_info = await gemini_service.extract_from_text(parsed_text=parsed_text)

        ...


    finally:
        await celery_async_engine.dispose()

    


@celery_app.task
def process_parsed_lookup(lookup_id: int) -> None: 
    return asyncio.run(async_process_parsed_lookup(lookup_id=lookup_id))