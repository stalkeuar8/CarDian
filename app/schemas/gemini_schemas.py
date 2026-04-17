from pydantic import BaseModel, ConfigDict

from app.schemas.lookups_schemas import CarSchema, ParsedLookupsRequestSchema


class GeminiAnalyzeResponseSchema(BaseModel):
    response: str


class GeminiAnalyzeRequestSchema(CarSchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    price_in_ad: int | None = None
    predicted_price: int



class GeminiExtractorRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    parsed_text: str

    
class GeminiExtractorResponseSchema(CarSchema):
    price_in_ad: int | None = None