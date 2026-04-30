from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.payment_schemas import PaymentRequestSchema, PaymentResponseSchema, PaymentSequenceResponseSchema, PaymentStatus
from app.repo.payments_repo import PaymentsRepo
from app.repo.users_repo import UsersRepo
from app.models.users import Users, Payments
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user
from app.utils.rate_limiter import rate_limiter

payments_router = APIRouter(prefix="/api/v1/users/payments", tags=['Users'])

@payments_router.get("/", summary="Get current user payments", response_model=PaymentSequenceResponseSchema)
@rate_limiter.limit("3/15 seconds") 
async def get_user_payments(request: Request, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> PaymentSequenceResponseSchema:
    payments: Sequence[Payments] | None = await PaymentsRepo.find_by_user_id(session=session, current_user_id=current_user.id)

    if payments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payments of user {current_user.id} were not found")

    return PaymentSequenceResponseSchema(items=[PaymentResponseSchema.model_validate(payment) for payment in payments], total_items_qty=len(payments))


@payments_router.get("/{payment_id}", summary="Get current user payment by id", response_model=PaymentResponseSchema)
@rate_limiter.limit("3/15 seconds") 
async def get_payment_by_id(request: Request, payment_id: int, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> PaymentResponseSchema:
    payment: Payments | None = await PaymentsRepo.find_by_id(session=session, current_user_id=current_user.id, id_to_find=payment_id)

    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment with id {payment_id} was not found")

    return PaymentResponseSchema.model_validate(payment)



@payments_router.patch("/", summary="Complete payment after processing (credit the tokens)", response_model=PaymentResponseSchema)
@rate_limiter.limit("3/15 seconds") 
async def complete_payment(request: Request, body: PaymentRequestSchema, current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> PaymentResponseSchema:
    payment: Payments | None = await PaymentsRepo.create(session=session, new_obj_dto=body)

    if payment is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Payment was not created, try later")

    raw_payment_schema = PaymentResponseSchema.model_validate(payment)

    user_info: Users | None = await UsersRepo.change_balance(session=session, user_id=current_user.id, tokens_change=raw_payment_schema.RATE.tokens)

    if user_info is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Payment was not created, try later")

    payment = await session.get(Payments, payment.id)
    payment.status = PaymentStatus.success

    payment_schema = PaymentResponseSchema.model_validate(payment)

    return payment_schema


