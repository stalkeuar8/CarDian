from pydantic import BaseModel, ConfigDict

from app.schemas.lookups_schemas import CarSchema


class GroqAnalyzeResponseSchema(BaseModel):
    response: str


class GroqAnalyzeRequestSchema(CarSchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    price_in_ad: int | None = None
    predicted_price: int



class GroqExtractorRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    parsed_text: str

    
class GroqExtractorResponseSchema(CarSchema):
    price_in_ad: int | None = None