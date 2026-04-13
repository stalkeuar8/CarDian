import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.prediction_schemas import BasePredictor
from app.schemas.lookups_schemas import ManualLookupRequestSchema, ManualLookupResponseSchema, ParsedLookupsRequestSchema, ParsedLookupsResponseSchema
from app.schemas.users_schemas import UserResponseSchema, EmailChangeRequestSchema, FullNameChangeRequestSchema, PasswordChangeRequestSchema, DeleteUserRequestSchema, DeleteUserResponseSchema
from app.repo.admin_repo.admin_users import AdminUsersRepo
from app.repo.lookups_repo import ManualLookupsRepo, ParsedLookupsRepo
from app.models.lookups import ManualLookups, ParsedLookupsRawData, ParsedLookups
from app.models.users import Users
from app.services.price_prediction import predict_service
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user, oauth2_scheme, decode_jwt
from app.utils.password_hasher import get_password_hash
from app.settings.redis import get_redis


lookups_routers = APIRouter(prefix="/v1/lookups", tags=['Lookups'])


@lookups_routers.post("/manual", summary="New manual lookup")
async def manual_lookup(body: ManualLookupRequestSchema, current_user: Users = Depends(get_current_user), redis: Redis = Depends(get_redis), session: AsyncSession = Depends(get_db)) -> !!!!!!!!!
    #rate limiting
    
    new_lookup: ManualLookups | None = await ManualLookupsRepo.create(session=session, new_obj_dto=body)

    if not new_lookup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant create new manual lookup")
    
    car_info_to_predict = BasePredictor(**body.model_dump())

    await predict_service.predict(data_to_predict=car_info_to_predict)

    await redis.set()