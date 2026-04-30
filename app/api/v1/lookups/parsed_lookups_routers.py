from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from app.schemas.verdicts_schemas import VerdictResponseSchema
from app.models.verdicts import Verdicts
from app.repo.verdicts_repo import VerdictsRepo
from app.schemas.lookups_schemas import LookupsPrices, ParsedLookupsCreateSchema, SequenceParsedLookupResponseSchema, ParsedLookupAcceptedSchema, ParsedLookupsRequestSchema, ParsedLookupsResponseSchema
from app.repo.lookups_repo import ParsedLookupsRepo
from app.models.lookups import ParsedLookups
from app.models.users import Users
from app.services.price_prediction import predict_service
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user
from app.background.lookups_processing_tasks import process_parsed_lookup
from app.utils.rate_limiter import rate_limiter


parsed_lookups_router = APIRouter(prefix="/v1/lookups/parsed", tags=['Parsed Lookups'])


@parsed_lookups_router.post("/", summary="New parsed lookups", response_model=ParsedLookupAcceptedSchema)
@rate_limiter.limit("5/15 seconds") 
async def new_parsed_lookup(request: Request, body: ParsedLookupsRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> ParsedLookupAcceptedSchema:
    
    if current_user.current_balance < LookupsPrices.parsed:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=f"Not enough tokens for this lookups")
    
    new_obj_dto = ParsedLookupsCreateSchema(url=body.url, user_id=current_user.id)
    
    new_lookup: ParsedLookups | None = await ParsedLookupsRepo.create(session=session, new_obj_dto=new_obj_dto)

    if new_lookup is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant create new parsed lookup")

    await session.commit()

    task = process_parsed_lookup.delay(new_lookup.id)

    return ParsedLookupAcceptedSchema(lookup_id=new_lookup.id, user_id=current_user.id, task_id=task.id, status_code=status.HTTP_202_ACCEPTED)


@parsed_lookups_router.get("/{lookup_id}/verdict", summary="Get parsed lookup verdict (polling)", response_model=VerdictResponseSchema)
@rate_limiter.limit("12/15 seconds")
async def get_verdict_parsed(request: Request, lookup_id: int, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> VerdictResponseSchema | JSONResponse:
    verdict: Verdicts | None = await VerdictsRepo.get_by_parsed_lookup_id(parsed_lookup_id=lookup_id, session=session, user_id=current_user.id)

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
        llm_feedback=verdict.llm_feedback,
        parsed_lookup_id=lookup_id
    )


@parsed_lookups_router.get("/{lookup_id}", summary="Get parsed lookup by id", response_model=ParsedLookupsResponseSchema)
@rate_limiter.limit("5/15 seconds") 
async def get_users_parsed_lookup_by_id(request: Request, lookup_id: int, session: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_user)) -> ParsedLookupsResponseSchema:
    lookup: ParsedLookups | None = await ParsedLookupsRepo.find_by_id(current_user_id=current_user.id, id_to_find=lookup_id, session=session)

    if lookup is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Parsed lookup with ID: {lookup_id} of this user was not found")
    
    return ParsedLookupsResponseSchema.model_validate(lookup)



@parsed_lookups_router.get("/my", summary="Get all users parsed lookups", response_model=SequenceParsedLookupResponseSchema)
@rate_limiter.limit("5/15 seconds")
async def get_all_users_parsed_lookups(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> SequenceParsedLookupResponseSchema:
    lookups: Sequence[ParsedLookups] | None = await ParsedLookupsRepo.get_all_users_lookups(user_id=current_user.id, session=session)

    if lookups is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user does not have any parsed lookups.")
    
    return SequenceParsedLookupResponseSchema(items=[ParsedLookupsResponseSchema.model_validate(item) for item in lookups], total_items_qty=len(lookups))



