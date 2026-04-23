import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import Sequence
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from app.schemas.verdicts_schemas import VerdictResponseSchema
from app.schemas.prediction_schemas import BasePredictor
from app.models.verdicts import Verdicts
from app.repo.verdicts_repo import VerdictsRepo
from app.schemas.lookups_schemas import SequenceManualLookupResponseSchema, ManualLookupRequestSchema, ManualLookupResponseSchema, ParsedLookupsRequestSchema, ParsedLookupsResponseSchema, ManualLookupAcceptedResponseSchema
from app.repo.lookups_repo import ManualLookupsRepo, ParsedLookupsRepo
from app.models.lookups import ManualLookups, ParsedLookupsRawData, ParsedLookups
from app.models.users import Users
from app.services.price_prediction import predict_service
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user, oauth2_scheme, decode_jwt
from app.utils.password_hasher import get_password_hash
from app.settings.redis import get_redis
from app.background.lookups_processing_tasks import process_manual_lookup
from app.utils.rate_limiter import rate_limiter

manual_lookups_router = APIRouter(prefix="/v1/lookups/manual", tags=['Manual Lookups'])


@manual_lookups_router.post("/", summary="New manual lookup", response_model=ManualLookupAcceptedResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def manual_lookup(request: Request, body: ManualLookupRequestSchema, current_user: Users = Depends(get_current_user), redis: Redis = Depends(get_redis), session: AsyncSession = Depends(get_db)) -> ManualLookupAcceptedResponseSchema:
    #rate limiting
    
    new_lookup: ManualLookups | None = await ManualLookupsRepo.create(session=session, new_obj_dto=body)

    if not new_lookup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant create new manual lookup")

    task = process_manual_lookup.delay(lookup_id=new_lookup.id)

    return ManualLookupAcceptedResponseSchema(status_code=status.HTTP_202_ACCEPTED, task_id=task.id, user_id=current_user.id, lookup_id=new_lookup.id)


@manual_lookups_router.get("/verdict/{lookup_id}", summary="Get manual lookup verdict (polling)", response_model=VerdictResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_verdict_manual(request: Request, lookup_id: int, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> VerdictResponseSchema | JSONResponse:
    verdict: Verdicts | None = await VerdictsRepo.get_by_manual_lookup_id(manual_lookup_id=lookup_id, session=session, user_id=current_user.id)

    if verdict is None:
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content="Still processing, continue polling.")
    
    predicted_price = verdict.predicted_price

    lower_bar = int(round(predicted_price - predicted_price*0.02, -2))
    upper_bar = int(round(predicted_price + predicted_price*0.02, -2))

    return VerdictResponseSchema(
        id=verdict.id,
        predicted_price=verdict.predicted_price,
        lower_bar=lower_bar,
        upper_bar=upper_bar,
        verdict=verdict.verdict,
        llm_feedback=verdict.llm_feedback,
        manual_lookup_id=lookup_id
    )


@manual_lookups_router.get("/{lookup_id}", summary="Get lookup by id", response_model=ManualLookupResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_users_manual_lookup_by_id(request: Request, lookup_id: int, session: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)) -> ManualLookupResponseSchema:
    lookup: ManualLookups | None = await ManualLookupsRepo.find_by_id(current_user_id=current_user.id, id_to_find=lookup_id, session=session)

    if lookup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Manual lookup with ID: {lookup_id} of this user was not found")
    
    return ManualLookupResponseSchema.model_validate(lookup)



@manual_lookups_router.get("/my", summary="Get all users manual lookups", response_model=SequenceManualLookupResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_all_users_manual_lookups(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> SequenceManualLookupResponseSchema:
    lookups: Sequence[ManualLookups] | None = await ManualLookupsRepo.get_all_users_lookups(user_id=current_user.id, session=session)

    if lookups is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user does not have any manual lookups.")
    
    return SequenceManualLookupResponseSchema(items=[ManualLookupResponseSchema.model_validate(item) for item in lookups], total_items_qty=len(lookups))



