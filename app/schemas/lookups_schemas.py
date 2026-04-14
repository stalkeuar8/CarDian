from pydantic import BaseModel, EmailStr, Field, field_validator, UrlConstraints, AnyUrl, AfterValidator

from typing import Annotated

from app.schemas.lookup_enums import BoolType, Condition, DriveTrainTypes, BodyTypes, ParsedLookupsStatus, ManualLookupsMode, FuelCategories, TransmissionType

from datetime import datetime


HttpsUrl = Annotated[
    AnyUrl, 
    UrlConstraints(allowed_schemes=['https'], host_required=True),
    AfterValidator(str)
]



class CarSchema(BaseModel):
    brand: str
    model: str
    year: int = Field(gt=1850)
    mileage_km: int = Field(ge=0)
    fuel_category: FuelCategories
    transmission: TransmissionType
    condition: Condition
    power_kw: int = Field(gt=0)
    body_type: BodyTypes
    drive_train: DriveTrainTypes
    had_accident: BoolType
    has_full_service_history: BoolType
    previous_owners_qty: int = Field(ge=0)
    seller_is_dealer: BoolType




class LookupBaseRequestSchema(CarSchema):
    user_id: int


class LookupBaseResponseSchema(LookupBaseRequestSchema):
    id: int
    status: str
    price_listed: int = Field(ge=0)
    created_at: datetime
    deleted_at: datetime


class ManualLookupSentResponseSchema(BaseModel):
    lookup_id: int
    user_id: int
    task_id: str
    status_code: int

class ManualLookupRequestSchema(LookupBaseRequestSchema):
    pass


class ManualLookupResponseSchema(LookupBaseResponseSchema):
    pass


class ParsedLookupsRequestSchema(LookupBaseRequestSchema):
    url: HttpsUrl


class ParsingResultSchema(BaseModel):
    raw_data: str
    request_data: ParsedLookupsRequestSchema


class ParsedLookupsResponseSchema(ParsedLookupsRequestSchema):
    pass