from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

from app.schemas.users_schemas import UserResponseSchema
from app.models.users import Users


users_router = APIRouter(prefix="/v1/users", tags=['Users'])

# @users_router.get("/profile", summary="Get current user profile", response_model=UserResponseSchema)
# async def get_my_profile(current_user: Users = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> Users:
#     return UserResponseSchema.model_validate(current_user)