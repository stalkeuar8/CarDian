from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    guest = "guest"


class UserBaseSchema(BaseModel):
    full_name: str
    email: EmailStr


class UserRegisterRequestSchema(UserBaseSchema):
    password: str


class UserCreateSchema(UserBaseSchema):
    hashed_password: str