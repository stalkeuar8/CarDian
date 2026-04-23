from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, model_validator
from enum import Enum
from datetime import datetime
from typing import Sequence, Self

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


class UserAdminResponseSchema(UserResponseSchema):
    deleted_at: datetime | None


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


class UserSequenceResponseSchema(BaseModel):
    items: Sequence[UserResponseSchema]
    total_items_qty: int

        
    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self