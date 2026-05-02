import asyncio

from app.background.celery_worker import celery_app
from app.models.lookups import ManualLookups, ParsedLookups, ParsedLookupsRawData
from app.services.price_prediction import predict_service
from app.models.verdicts import Verdicts
from app.models.users import Users
from app.repo.lookups_repo import ParsedLookupsRepo
from app.schemas.lookup_enums import ManualLookupsStatus, ParsedLookupsStatus
from app.schemas.lookups_schemas import CarSchema, ParsedLookupUpdatingSchema, LookupsPrices
from app.schemas.groq_schemas import GroqAnalyzeRequestSchema, GroqAnalyzeResponseSchema, GroqExtractorRequestSchema, GroqExtractorResponseSchema
from app.settings.config import database_settings
from app.services.gemini_service import gemini_service
from app.services.groq_service import groq_service
from app.services.parse_service import parse_service

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from google.api_core.exceptions import ServiceUnavailable, ResourceExhausted, DeadlineExceeded

import logging
import sys

logging.basicConfig(
    level=logging.INFO,  
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def async_process_manual_lookup(self, lookup_id: int) -> None:

    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    lookup = None
    # logger.info("before try")
    try:
        
        async with celery_async_session_factory.begin() as session:
            lookup_info: ManualLookups | None = await session.get(ManualLookups, lookup_id)
            
            if lookup_info is None:
                raise ValueError(f"Manual Lookup with ID: {lookup_id} was not found")
            
            lookup = lookup_info

            car_info = CarSchema.model_validate(lookup)
        # logger.info("lookup found")
        
        try:
            predicted_price = predict_service.predict(data_to_predict=car_info)
        
        except Exception as e:
            logger.error(f"predicting error: {e}")

        info_to_analyze = GroqAnalyzeRequestSchema(**car_info.model_dump(), predicted_price=predicted_price)


        try:

            llm_result: GroqAnalyzeResponseSchema = await groq_service.analyze_existing(info_to_analyze)
            # logger.info(f"groq completed, : {llm_result}")
            
            llm_feedback = llm_result.response
            is_groq_completed = True
            # logger.info(f"groq completed, feedback: {llm_feedback}")
        except Exception as e:
            logger.error(f"groq error: {e}")
            is_groq_completed = False
            llm_feedback = None

        verdict = Verdicts(
            manual_lookup_id=lookup_id, 
            predicted_price=predicted_price,
            llm_feedback=llm_feedback
        )

        async with celery_async_session_factory.begin() as session:
            # logger.info("session started")
            session.add(verdict)
            # logger.info("verdict added")
            
            lookup: ManualLookups | None = await session.get(ManualLookups, lookup_id)

            if is_groq_completed:
                lookup.status = ManualLookupsStatus.completed
            else:
                lookup.status = ManualLookupsStatus.groq_failed

            lookup.price_listed = predicted_price

            # logger.info("lookup updated")
            user: Users | None = await session.get(Users, lookup.user_id)

            if user is None:
                logger.error("user was not found")
                raise ValueError(f"User with ID: {lookup.user_id} was not found")

            user.current_balance = user.current_balance-LookupsPrices.manual
            logger.info("session ended")

    except (ServiceUnavailable, DeadlineExceeded) as e:
        logger.error(f"ERROR: {e}")
        raise self.retry(exc=e, countdown=10)

    except (Exception, ResourceExhausted) as e: 
        logger.info(f"Error, manual lookup id: {lookup_id}:  {e}", exc_info=True)
        
        async with celery_async_session_factory.begin() as session:
            lookup: ManualLookups = await session.get(ManualLookups, lookup_id)
            lookup.status = ManualLookupsStatus.failed

    finally:
        await celery_async_engine.dispose()


@celery_app.task(
    bind=True,
    autoretry_for=(ServiceUnavailable, DeadlineExceeded,),
    retry_backoff=True,
    retry_kwargs={"max_retries":5},
    retry_jitter=True
)
def process_manual_lookup(self, lookup_id: int) -> None:
    return asyncio.run(async_process_manual_lookup(self=self, lookup_id=lookup_id))



async def async_process_parsed_lookup(self, lookup_id: int) -> None:
    celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

    celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

    parsed_lookup = None
    # logger.info("before try")
    try:
        async with celery_async_session_factory.begin() as session:
            lookup: ParsedLookups | None = await session.get(ParsedLookups, lookup_id)

            if lookup is None:
                raise ValueError(f"Parsed Lookup with ID: {lookup_id} was not found")

            parsed_lookup = lookup
        # logger.info("lookups found")

        parsed_text = await parse_service.process_url(url=parsed_lookup.url)
        # logger.info(f"text parsed: {parsed_text}")
        parsed_car_info: GroqExtractorResponseSchema | None = await groq_service.extract_from_text(parsed_data=GroqExtractorRequestSchema(parsed_text=parsed_text))
        # logger.info(f"json: {parsed_car_info}")

        if parsed_car_info is None:    
            raise ValueError("Invalid data, unable to extract")
        # logger.info(f"before predicting")

        predicted_price: int = predict_service.predict(data_to_predict=parsed_car_info)

        # logger.info(f"predicted price: {predicted_price}")
        
        info_to_analyze = GroqAnalyzeRequestSchema(**parsed_car_info.model_dump(), predicted_price=predicted_price)
        
        try:

            llm_result: GroqAnalyzeResponseSchema = await groq_service.analyze_existing(info_to_analyze)
            # logger.info(f"analyzing res: {llm_result}")
            llm_feedback = llm_result.response
            is_groq_completed = True
            
        except Exception as e:
            logger.error(f"ERROR: {e}")
            is_groq_completed = False
            llm_feedback = None

        verdict = Verdicts(
            parsed_lookup_id=lookup_id, 
            predicted_price=predicted_price,
            llm_feedback=llm_feedback
        )

        parsed_raw_data = ParsedLookupsRawData(
            parsed_lookup_id=lookup_id,
            raw_data=parsed_text
        )

        async with celery_async_session_factory.begin() as session:

            session.add(parsed_raw_data)    
            session.add(verdict)

            if is_groq_completed:
                status = ParsedLookupsStatus.completed
            else:
                status = ParsedLookupsStatus.groq_failed

            car_info = CarSchema(**parsed_car_info.model_dump())
            
            dto = ParsedLookupUpdatingSchema(
                car_info=car_info,
                price_listed=predicted_price,
                status=status
            )

            updated_lookup = await ParsedLookupsRepo.update_after_analyzing(lookup_id=lookup_id, session=session, updated_info=dto)
            
            user: Users | None = await session.get(Users, lookup.user_id)

            if user is None:
                raise ValueError(f"User with ID: {lookup.user_id} was not found")

            user.current_balance = user.current_balance-LookupsPrices.parsed

    except (ServiceUnavailable, DeadlineExceeded) as e:
        logger.error(f"ERROR: {e}")
        raise self.retry(exc=e, countdown=10)

    except (Exception, ResourceExhausted) as e: 
        logger.info(f"Error, parsed lookup id: {lookup_id}:  {e}", exc_info=True)
        
        async with celery_async_session_factory.begin() as session:
            lookup: ParsedLookups = await session.get(ParsedLookups, lookup_id)
            lookup.status = ParsedLookupsStatus.failed

    finally:
        await celery_async_engine.dispose()


@celery_app.task(
    bind=True,
    autoretry_for=(ServiceUnavailable, DeadlineExceeded,),
    retry_backoff=True,
    retry_kwargs={"max_retries":5},
    retry_jitter=True
)
def process_parsed_lookup(self, lookup_id: int) -> None: 
    return asyncio.run(async_process_parsed_lookup(self=self, lookup_id=lookup_id))








# async def async_process_manual_lookup(self, lookup_id: int) -> None:

#     celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

#     celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

#     lookup = None

#     try:
        
#         async with celery_async_session_factory.begin() as session:
#             lookup_info: ManualLookups | None = await session.get(ManualLookups, lookup_id)
            
#             if lookup_info is None:
#                 raise ValueError(f"Manual Lookup with ID: {lookup_id} was not found")
            
#             lookup = lookup_info

#             car_info = CarSchema.model_validate(lookup)
        
#         predicted_price = predict_service.predict(data_to_predict=car_info)

#         info_to_analyze = GeminiAnalyzeRequestSchema(**car_info.model_dump(), predicted_price=predicted_price)
        
#         try:

#             gemini_result: GeminiAnalyzeResponseSchema = await gemini_service.analyze_existing(info_to_analyze)
            
#             llm_feedback = gemini_result.response
#             is_gemini_completed = True
            
#         except Exception as e:
#             is_gemini_completed = False
#             llm_feedback = None


#         verdict = Verdicts(
#             manual_lookup_id=lookup_id, 
#             predicted_price=predicted_price,
#             verdict=VerdictTypes.no_type,
#             llm_feedback=llm_feedback
#         )

#         async with celery_async_session_factory.begin() as session:
#             session.add(verdict)
            
#             lookup: ManualLookups | None = await session.get(ManualLookups, lookup_id)
#             if is_gemini_completed:
#                 lookup.status = ManualLookupsStatus.completed
#             else:
#                 lookup.status = ManualLookupsStatus.gemini_failed

#             lookup.price_listed = predicted_price


#     except (ServiceUnavailable, DeadlineExceeded) as e:
#         logger.error(f"ERROR: {e}")
#         raise self.retry(exc=e, countdown=10)

#     except (Exception, ResourceExhausted) as e: 
#         logger.info(f"Error, manual lookup id: {lookup_id}:  {e}", exc_info=True)
        
#         async with celery_async_session_factory.begin() as session:
#             lookup: ManualLookups = await session.get(ManualLookups, lookup_id)
#             lookup.status = ManualLookupsStatus.failed

#     finally:
#         await celery_async_engine.dispose()


# @celery_app.task(
#     bind=True,
#     autoretry_for=(ServiceUnavailable, DeadlineExceeded,),
#     retry_backoff=True,
#     retry_kwargs={"max_retries":5},
#     retry_jitter=True
# )
# def process_manual_lookup(self, lookup_id: int) -> None:
#     return asyncio.run(async_process_manual_lookup(self=self, lookup_id=lookup_id))



# async def async_process_parsed_lookup(self, lookup_id: int) -> None:
#     celery_async_engine: AsyncEngine = create_async_engine(url=database_settings.DATABASE_url, echo=False, poolclass=NullPool)

#     celery_async_session_factory = async_sessionmaker(celery_async_engine, expire_on_commit=False)

#     parsed_lookup = None

#     try:
#         async with celery_async_session_factory.begin() as session:
#             lookup: ParsedLookups | None = await session.get(ParsedLookups, lookup_id)

#             if lookup is None:
#                 raise ValueError(f"Parsed Lookup with ID: {lookup_id} was not found")

#             parsed_lookup = lookup

#         parsed_text = await parse_service.process_url(url=parsed_lookup.url)
        
#         parsed_car_info: GeminiExtractorResponseSchema | None = await gemini_service.extract_from_text(parsed_data=GeminiExtractorRequestSchema(parsed_text=parsed_text))
        
#         if parsed_car_info is None:    
#             raise ValueError("Invalid data, unable to extract")

#         predicted_price: int = predict_service.predict(data_to_predict=parsed_car_info)

#         info_to_analyze = GeminiAnalyzeRequestSchema(**parsed_car_info.model_dump(), predicted_price=predicted_price, price_in_ad=parsed_car_info.price_in_ad)
        
#         try:

#             gemini_result: GeminiAnalyzeResponseSchema = await gemini_service.analyze_existing(info_to_analyze)
            
#             llm_feedback = gemini_result.response
#             is_gemini_completed = True
            
#         except Exception as e:
#             is_gemini_completed = False
#             llm_feedback = None

#         verdict = Verdicts(
#             parsed_lookup_id=lookup_id, 
#             predicted_price=predicted_price,
#             verdict=VerdictTypes.no_type,
#             llm_feedback=llm_feedback
#         )

#         async with celery_async_session_factory.begin() as session:

#             session.add(verdict)
#             if is_gemini_completed:
#                 status = ParsedLookupsStatus.completed
#             else:
#                 status = ParsedLookupsStatus.gemini_failed

#             dto = ParsedLookupUpdatingSchema(
#                 car_info=parsed_car_info,
#                 price_listed=predicted_price,
#                 status=status
#             )

#             updated_lookup = await ParsedLookupsRepo.update_after_analyzing(lookup_id=lookup_id, session=session, updated_info=dto)
            
#     except (ServiceUnavailable, DeadlineExceeded) as e:
#         logger.error(f"ERROR: {e}")
#         raise self.retry(exc=e, countdown=10)

#     except (Exception, ResourceExhausted) as e: 
#         logger.info(f"Error, parsed lookup id: {lookup_id}:  {e}", exc_info=True)

        
#         async with celery_async_session_factory.begin() as session:
#             lookup: ParsedLookups = await session.get(ParsedLookups, lookup_id)
#             lookup.status = ParsedLookupsStatus.failed

#     finally:
#         await celery_async_engine.dispose()


# @celery_app.task(
#     bind=True,
#     autoretry_for=(ServiceUnavailable, DeadlineExceeded,),
#     retry_backoff=True,
#     retry_kwargs={"max_retries":5},
#     retry_jitter=True
# )
# def process_parsed_lookup(self, lookup_id: int) -> None: 
#     return asyncio.run(async_process_parsed_lookup(self=self, lookup_id=lookup_id))


