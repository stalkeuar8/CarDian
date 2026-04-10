from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.users_schemas import UserBaseSchema, UserResponseSchema
from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserRegisterRequestSchema(UserBaseSchema):
    password: str


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserAuthResponseSchema(UserResponseSchema):
    refresh_token: str
    access_token: str

    model_config = ConfigDict(from_attributes=True, extra="allow")


class UserLogoutResponseSchema(BaseModel):
    is_logged_out: bool
    status: int
    message: str


class UserRefreshRequestSchema(BaseModel):
    refresh_token: str


class UserRefreshResponseSchema(BaseModel):
    access_token: str
    refresh_token: str