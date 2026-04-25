from pydantic import BaseModel
from enum import Enum


class VerdictBaseSchema(BaseModel):
    predicted_price: int
    price_deviation_percent: int | None = None

    
class VerdictManualRequestSchema(VerdictBaseSchema):
    manual_lookup_id: int


class VerdictParsedRequestSchema(VerdictBaseSchema):
    parsed_lookup_id: int


class VerdictResponseSchema(VerdictBaseSchema):
    id: int
    lower_bar: int
    upper_bar: int
    llm_feedback: str | None = None
    manual_lookup_id: int | None = None
    parsed_lookup_id: int | None = None

