from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, UrlConstraints, AnyUrl, AfterValidator, Field


HttpsUrl = Annotated[
    AnyUrl, 
    UrlConstraints(allowed_schemes=['https'], host_required=True),
    AfterValidator(str)
]


class WatchlistBaseSchema(BaseModel):
    user_id: int
    url: HttpsUrl
    last_price: int = Field(ge=0)


class WatchlistRequestSchema(WatchlistBaseSchema):
    pass


class WatchlistResponseSchema(WatchlistBaseSchema):
    id: int
    is_active: bool
    created_at: datetime


