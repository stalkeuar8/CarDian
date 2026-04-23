from pydantic import BaseModel, Field

class StatsResponseSchema(BaseModel):
    total_manual_lookups: int = Field(ge=0)
    total_parsed_lookups: int = Field(ge=0)
    total_watchlist: int = Field(ge=0)
    total_price_alerts: int = Field(ge=0)
    total_users: int = Field(ge=0)

