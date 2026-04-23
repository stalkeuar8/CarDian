import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.users_schemas import UserAdminResponseSchema, UserSequenceResponseSchema, UserResponseSchema, EmailChangeRequestSchema, FullNameChangeRequestSchema, PasswordChangeRequestSchema, DeleteUserRequestSchema, DeleteUserResponseSchema
from app.schemas.stats_schema import StatsResponseSchema
from app.repo.admin_repo.admin_users import AdminUsersRepo
from app.models.users import Users
from app.settings.database import get_db
from app.auth.jwt_token import get_current_user, oauth2_scheme, decode_jwt, get_current_admin_user
from app.utils.password_hasher import get_password_hash
from app.settings.redis import get_redis
from app.utils.rate_limiter import rate_limiter

admin_router = APIRouter(prefix="/v1/admin", tags=['Admin'])

@admin_router.get("/users/{user_id}", summary="Get user by id (including deleted)", response_model=UserAdminResponseSchema)
async def get_users(user_id: int, get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> UserAdminResponseSchema:
    users: Users | None = await AdminUsersRepo.get_by_id(id_to_get=user_id, exclude_deleted=False, session=session)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} was not found")
    
    return UserAdminResponseSchema.model_validate(users)


@admin_router.get("/users/{user_email}", summary="Get user by email (including deleted)", response_model=UserAdminResponseSchema)
async def get_users(user_email: int, get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> UserAdminResponseSchema:
    users: Users | None = await AdminUsersRepo.get_by_email(email_to_get=user_email, exclude_deleted=False, session=session)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email '{user_email}' was not found")
    
    return UserAdminResponseSchema.model_validate(users)


@admin_router.get("/stats", summary="Get all platform stats", response_model=StatsResponseSchema)
async def get_users(get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> StatsResponseSchema:
    