import uuid
import jwt
from typing import Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.settings.database import get_db
from app.settings.config import jwt_settings
from app.models.users import Users
from app.settings.redis import get_redis
from app.schemas.users_schemas import UserRole
from app.schemas.auth_schemas import TokenType
from app.repo.admin_repo.admin_users import AdminUsersRepo

ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer("/api/v1/auth/login")
REFRESH_EXPIRES = jwt_settings.REF_EXP_TIME
ACCESS_EXPIRES = jwt_settings.ACC_EXP_TIME

def create_token(user_id: int, token_type: TokenType) -> str:
    
    if token_type == TokenType.ACCESS:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_EXPIRES)
    else:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=REFRESH_EXPIRES)


    jti = str(uuid.uuid4())

    payload = {
        "sub" : str(user_id),
        "type" : token_type.value,
        "exp" : expires_at,
        "jti" : jti
    }

    encoded_jwt = jwt.encode(payload=payload, algorithm=ALGORITHM, key=jwt_settings.SECRETKEY)

    return encoded_jwt



def decode_jwt(jwt_token: str) -> dict[str, Any]:

    try:
        
        payload = jwt.decode(jwt=jwt_token, key=jwt_settings.SECRETKEY, algorithms=[ALGORITHM])

        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    

async def get_current_user(jwt_token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db), redis=Depends(get_redis)) -> Users:
    payload = decode_jwt(jwt_token=jwt_token)

    token_type = payload.get("type", None)
    user_id = payload.get("sub", None)
    jti = payload.get("jti", None)

    if token_type is None or token_type != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token type is invalid")

    if user_id is None or jti is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")

    token_in_redis = await redis.get(f"blacklist:{jti}")

    if token_in_redis:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is in blacklist (logged)")
    
    user: Users | None = await AdminUsersRepo.get_by_id(session=session, id_to_get=int(user_id), exclude_deleted=True)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT AUTH Error, can not find user")
    
    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)) -> Users:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required.")
    
    return current_user

