from typing import Annotated, Sequence, Self
from datetime import datetime
from pydantic import BaseModel, UrlConstraints, AnyUrl, AfterValidator, Field, model_validator, ConfigDict, PlainSerializer


HttpsUrl = Annotated[
    AnyUrl, 
    UrlConstraints(allowed_schemes=['https'], host_required=True),
    AfterValidator(str),
    PlainSerializer(lambda x: str(x), return_type=str)
]


class WatchlistBaseSchema(BaseModel):
    url: HttpsUrl
    last_price: int = Field(ge=0)


class WatchlistRequestSchema(WatchlistBaseSchema):
    pass


class WatchlistCreateSchema(WatchlistRequestSchema):
    user_id: int


class WatchlistResponseSchema(WatchlistBaseSchema):
    model_config = ConfigDict(extra='allow', from_attributes=True)
    user_id: int
    id: int
    is_active: bool
    created_at: datetime


class WatchlistSequenceResponseSchema(BaseModel):
    items: Sequence[WatchlistResponseSchema]
    total_items_qty: int

    @model_validator(mode='after')
    def validate_qty(self) -> Self:
        total_length = len(self.items)
        self.total_items_qty = total_length

        return self
