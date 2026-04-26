from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
from typing import Self, Sequence

class PriceAlertsBaseSchema(BaseModel):

    watchlist_id: int = Field(gt=0)
    price_diff: int 
    price_diff_percents: int 

    @classmethod
    @field_validator("price_diff")
    def validate_price_diff(cls, value: int) -> int:
        if value == 0:
            raise ValueError("Price difference can not be 0.")
        
        return value
    
    @classmethod
    @field_validator("price_diff_percents")
    def validate_percents(cls, value: int) -> int:
        if not 0 < value <= 100 or not 0 > value >= -100:
            raise ValueError("Percent price difference can be between (0 and 100) or (0 and -100)") 
    

class PriceAlertRequestSchema(PriceAlertsBaseSchema):
    pass


class PriceAlertResponseSchema(PriceAlertsBaseSchema):
    model_config = ConfigDict(from_attributes=True, extra='ignore')

    id: int
    is_sent: bool
    noticed_at: datetime
    

class PriceAlertSequenceResponseSchema(BaseModel):
    items: Sequence[PriceAlertResponseSchema]
    total_items_qty: int

    
    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self