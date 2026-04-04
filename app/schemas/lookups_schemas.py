from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.lookup_enums import ParsedLookupsStatus, ManualLookupsMode, FuelType, TransmissionType

from datetime import datetime

class LookupBaseSchema(BaseModel):
    user_id: int
    brand: str
    model: str
    year: int = Field(gt=1850)
    mileage: int = Field(ge=0)
    fuel_type: FuelType
    transmission: TransmissionType
    condition: int = Field(ge=1, le=10)
    price_listed: int = Field(ge=0)


class ManualLookupRequestSchema(LookupBaseSchema):
    mode: ManualLookupsMode


class ManualLookupResponseSchema(ManualLookupRequestSchema):
    id: int
    created_at: datetime


class ParsedLookupsRequestSchema(LookupBaseSchema):
    status: ParsedLookupsStatus
    raw_data: str

class ParsedLookupsResponseSchema(ParsedLookupsRequestSchema):
    id: int
    created_at: datetime
