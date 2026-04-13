from pydantic import BaseModel, ConfigDict, Field
from app.schemas.lookups_schemas import CarSchema

class BasePredictor(CarSchema):
    model_config = ConfigDict(from_attributes=True, extra='allow')



