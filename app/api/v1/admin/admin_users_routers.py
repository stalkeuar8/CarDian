from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from app.schemas.users_schemas import UserAdminResponseSchema
from app.repo.admin_repo.admin_users import AdminUsersRepo
from app.models.users import Users
from app.settings.database import get_db
from app.auth.jwt_token import get_current_admin_user
from app.utils.rate_limiter import rate_limiter

admin_users_router = APIRouter(prefix="/api/v1/admin/users", tags=['Admin (Users)'])

@admin_users_router.get("/{user_id}", summary="Get user by id (including deleted)", response_model=UserAdminResponseSchema)
@rate_limiter.limit("100/15 seconds") 
async def get_users(request: Request, user_id: int, get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> UserAdminResponseSchema:
    users: Users | None = await AdminUsersRepo.get_by_id(id_to_get=user_id, exclude_deleted=False, session=session)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} was not found")
    
    return UserAdminResponseSchema.model_validate(users)


@admin_users_router.get("/{user_email}", summary="Get user by email (including deleted)", response_model=UserAdminResponseSchema)
@rate_limiter.limit("100/15 seconds") 
async def get_users(request: Request, user_email: int, get_current_admin_users: Users = Depends(get_current_admin_user), session: AsyncSession = Depends(get_db)) -> UserAdminResponseSchema:
    users: Users | None = await AdminUsersRepo.get_by_email(email_to_get=user_email, exclude_deleted=False, session=session)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email '{user_email}' was not found")
    
    return UserAdminResponseSchema.model_validate(users)

#user stats



# @admin_users_router.delete("/me", summary="Deactivate users profile", response_model=DeleteUserResponseSchema)
# @rate_limiter.limit("100/15 seconds") 
# async def deactivate_user_profile(request: Request, body: DeleteUserRequestSchema, jwt_token: str = Depends(oauth2_scheme), current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)) -> DeleteUserResponseSchema:
    
#     deleted_user: Users | None = await AdminUsersRepo.soft_delete_user(session=session, user_id=current_user.id)

#     if not deleted_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is already deleted or not found")
    
#     await redis.delete(f"refresh:{deleted_user.id}") 
    
#     payload = decode_jwt(jwt_token=jwt_token)
#     jti = payload.get("jti", None)
#     exp = payload.get("exp", None)

#     if jti is None or exp is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
        
#     current_time_seconds = int(datetime.now(tz=timezone.utc).timestamp())
#     time_left = exp - current_time_seconds

#     if time_left > 0:
#         await redis.set(f"blacklist:{jti}", "1", ex=time_left)

#     return DeleteUserResponseSchema(is_deleted=True, deleted_at=deleted_user.deleted_at)