from pydantic import BaseModel, EmailStr, Field, PlainSerializer, UrlConstraints, AnyUrl, AfterValidator, ConfigDict, model_validator, BeforeValidator

from typing import Annotated, Sequence, Self

from app.schemas.lookup_enums import BoolType, Condition, DriveTrainTypes, BodyTypes, ParsedLookupsStatus, FuelCategories, TransmissionType

from datetime import datetime


HttpsUrl = Annotated[
    AnyUrl, 
    UrlConstraints(allowed_schemes=['https'], host_required=True),
    AfterValidator(str),
    PlainSerializer(lambda x: str(x), return_type=str)
]


class CarSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    
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


class LookupAccepted(BaseModel):
    lookup_id: int
    user_id: int
    task_id: str
    status_code: int


class ManualLookupAcceptedResponseSchema(LookupAccepted):
    pass


class ManualLookupRequestSchema(LookupBaseRequestSchema):
    pass


class ManualLookupResponseSchema(LookupBaseResponseSchema):
    pass


class SequenceManualLookupResponseSchema(BaseModel):
    items: Sequence[ManualLookupResponseSchema]
    total_items_qty: int

    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self


class ParsedLookupsRequestSchema(BaseModel):
    url: HttpsUrl


class ParsedLookupsCreateSchema(ParsedLookupsRequestSchema):
    user_id: int


class ParsedLookupsResponseSchema(LookupBaseResponseSchema, ParsedLookupsRequestSchema):
    pass


class ParsedLookupAcceptedSchema(LookupAccepted):
    pass


class ParsingResultSchema(BaseModel):
    raw_data: str
    parsed_lookup_id: int


class ParsedLookupUpdatingSchema(BaseModel):
    car_info: CarSchema
    price_listed: int
    status: ParsedLookupsStatus

class SequenceParsedLookupResponseSchema(BaseModel):
    items: Sequence[ParsedLookupsResponseSchema]
    total_items_qty: int

    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self