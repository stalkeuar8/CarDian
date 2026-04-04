from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str, non_empty_int
from app.schemas.users_schemas import UserRole

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Index



class ManualLookups(Base):

    __tablename__ = "manual_lookups"

    id: Mapped[idpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), index=True)
    mode: Mapped[non_empty_str] = mapped_column(index=True)
    brand: Mapped[non_empty_str] = mapped_column(index=True)
    model: Mapped[non_empty_str] = mapped_column(index=True)
    year: Mapped[non_empty_int]
    mileage: Mapped[non_empty_int] 
    fuel_type: Mapped[non_empty_str]
    transmission: Mapped[non_empty_str]
    condition: Mapped[non_empty_int]
    price_listed: Mapped[non_empty_int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))

    __table_args__ = (
        Index("brand_model_idx", "brand", "model"),
    )


class ParsedLookups(Base):

    __tablename__ = "parsed_lookups"

    id: Mapped[idpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), index=True)
    status: Mapped[non_empty_str]
    raw_data: Mapped[str]
    brand: Mapped[non_empty_str] = mapped_column(index=True)
    model: Mapped[non_empty_str] = mapped_column(index=True)
    year: Mapped[non_empty_int]
    mileage: Mapped[non_empty_int] 
    fuel_type: Mapped[non_empty_str]
    transmission: Mapped[non_empty_str]
    condition: Mapped[non_empty_int]
    price_listed: Mapped[non_empty_int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))

    __table_args__ = (
        Index("brand_model_idx", "brand", "model"),
    )