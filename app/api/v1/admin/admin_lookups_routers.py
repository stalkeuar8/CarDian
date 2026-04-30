from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request

from app.schemas.verdicts_schemas import VerdictResponseSchema
from app.models.verdicts import Verdicts
from app.repo.verdicts_repo import AdminVerdictsRepo
from app.models.users import Users
from app.services.price_prediction import predict_service
from app.settings.database import get_db
from app.auth.jwt_token import get_current_admin_user
from app.utils.rate_limiter import rate_limiter

admin_lookups_router = APIRouter(prefix="/v1/admin/lookups", tags=['Admin (Lookups)'])


@admin_lookups_router.get("/manual/{lookup_id}/verdict", summary="Admin - Get manual lookup verdict ", response_model=VerdictResponseSchema)
@rate_limiter.limit("100/10 seconds")
async def admin_get_verdict_manual(request: Request, lookup_id: int, current_user: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> VerdictResponseSchema | JSONResponse:
    verdict: Verdicts | None = await AdminVerdictsRepo.get_by_manual_lookup_id(manual_lookup_id=lookup_id, session=session)

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
        manual_lookup_id=lookup_id
    )


# @admin_lookups_router.get("/{lookup_id}", summary="Admin - Get lookup by id", response_model=ManualLookupResponseSchema)
# @rate_limiter.limit("100/10 seconds")
# async def admin_get_users_manual_lookup_by_id(request: Request, lookup_id: int, session: AsyncSession = Depends(get_db), current_user: Users = Depends(get_current_admin_user)) -> ManualLookupResponseSchema:
#     lookup: ManualLookups | None = await ManualLookupsRepo.find_by_id(current_user_id=current_user.id, id_to_find=lookup_id, session=session)

#     if lookup is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Manual lookup with ID: {lookup_id} of this user was not found")
    
#     return ManualLookupResponseSchema.model_validate(lookup)


# @admin_lookups_router.get("/users/manual", summary="Admin - Get all users manual lookups", response_model=SequenceManualLookupResponseSchema)
# @rate_limiter.limit("5/15 seconds")
# async def get_all_users_manual_lookups(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> SequenceManualLookupResponseSchema:
#     lookups: Sequence[ManualLookups] | None = await ManualLookupsRepo.get_all_users_lookups(user_id=current_user.id, session=session)

#     if lookups is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user does not have any manual lookups.")
    
#     return SequenceManualLookupResponseSchema(items=[ManualLookupResponseSchema.model_validate(item) for item in lookups], total_items_qty=len(lookups))


# @admin_lookups_router.get("/users/manual/{lookup_id}", summary="Admin - Get users manual lookup by id", response_model=SequenceManualLookupResponseSchema)
# @rate_limiter.limit("5/15 seconds")
# async def get_all_users_manual_lookups(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> SequenceManualLookupResponseSchema:
#     lookups: Sequence[ManualLookups] | None = await ManualLookupsRepo.get_all_users_lookups(user_id=current_user.id, session=session)

#     if lookups is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user does not have any manual lookups.")
    
#     return SequenceManualLookupResponseSchema(items=[ManualLookupResponseSchema.model_validate(item) for item in lookups], total_items_qty=len(lookups))



