from pydantic import BaseModel
from enum import Enum

class VerdictTypes(str, Enum):
    clean = "clean"
    suspicious = "suspicious"
    dangerous = "dangerous"


class VerdictBaseSchema(BaseModel):
    predicted_price: int
    price_deviation_percent: int
    verdict: VerdictTypes
    llm_feedback: str

    
class VerdictManualRequestSchema(VerdictBaseSchema):
    manual_lookup_id: int


class VerdictParsedRequestSchema(VerdictBaseSchema):
    parsed_lookup_id: int


class VerdictResponseSchema(VerdictBaseSchema):
    id: int
    manual_lookup_id: int | None = None
    parsed_lookup_id: int | None = None

