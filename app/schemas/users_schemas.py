from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    guest = "guest"


class UserBaseSchema(BaseModel):
    full_name: str
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    hashed_password: str

    model_config = ConfigDict(extra='ignore')


class UserResponseSchema(UserBaseSchema):
    id: int
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailChangeRequestSchema(BaseModel):
    new_email: EmailStr


class FullNameChangeRequestSchema(BaseModel):
    new_full_name: str

class PasswordChangeRequestSchema(BaseModel):
    old_password: str
    new_password: str


class DeleteUserRequestSchema(BaseModel):
    current_password: str

class DeleteUserResponseSchema(BaseModel):
    is_deleted: bool
    deleted_at: datetime