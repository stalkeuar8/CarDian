from pydantic import BaseModel, EmailStr, ConfigDict
from app.schemas.users_schemas import UserBaseSchema, UserResponseSchema

class UserRegisterRequestSchema(UserBaseSchema):
    password: str


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserAuthResponseSchema(UserResponseSchema):
    jwt_token: str

    model_config = ConfigDict(from_attributes=True, extra="allow")