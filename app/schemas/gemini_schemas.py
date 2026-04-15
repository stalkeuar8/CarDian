from pydantic import BaseModel, ConfigDict

from app.schemas.lookups_schemas import CarSchema


class GeminiAnalyzeResponseSchema(BaseModel):
    response: str


class GeminiAnalyzeRequestSchema(CarSchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    predicted_price: int