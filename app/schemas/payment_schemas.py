from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Sequence, Self
from enum import Enum
from datetime import datetime

class PaymentStatus(str, Enum):
    success = "success"
    failed = "failed"
    pending = "pending"


class Rate(BaseModel):
    tokens: int = Field(ge=1)
    price: float = Field(ge=1)


class RateTypes(str, Enum):
    starter = "starter"
    pro = "pro"


class PaymentRequestSchema(BaseModel):
    rate: RateTypes  
    user_id: int

RATES = {
    RateTypes.starter : Rate(tokens=8, price=4.99),
    RateTypes.pro : Rate(tokens=100, price=39.99)
}

class PaymentResponseSchema(PaymentRequestSchema):
    model_config = ConfigDict(from_attributes=True, extra='ignore')
    
    id: int
    status: PaymentStatus
    created_at: datetime

    @property
    def RATE(self):
        if self.rate == RateTypes.starter:
            return RATES[RateTypes.starter]
        
        if self.rate == RateTypes.pro:
            return RATES[RateTypes.pro]
        

class PaymentSequenceResponseSchema(BaseModel):
    items: Sequence[PaymentResponseSchema]
    total_items_qty: int

    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self