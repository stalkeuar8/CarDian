import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.prediction_schemas import BasePredictor
from app.schemas.lookups_schemas import ManualLookupRequestSchema, ManualLookupResponseSchema, ParsedLookupsRequestSchema, ParsedLookupsResponseSchema, ManualLookupSentResponseSchema
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
from app.background.lookups_processing_tasks import process_manual_lookup


# verdicts_router = APIRouter(prefix=)