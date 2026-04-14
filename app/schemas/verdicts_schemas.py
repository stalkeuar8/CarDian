from pydantic import BaseModel
from enum import Enum

class VerdictTypes(str, Enum):
    clean = "clean"
    suspicious = "suspicious"
    dangerous = "dangerous"
    no_type = "no_type"

class VerdictBaseSchema(BaseModel):
    predicted_price: int
    price_deviation_percent: int | None = None
    verdict: VerdictTypes 

    
class VerdictManualRequestSchema(VerdictBaseSchema):
    manual_lookup_id: int


class VerdictParsedRequestSchema(VerdictBaseSchema):
    parsed_lookup_id: int


class VerdictResponseSchema(VerdictBaseSchema):
    id: int
    llm_feedback: str | None = None
    manual_lookup_id: int | None = None
    parsed_lookup_id: int | None = None

