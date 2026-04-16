from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str, non_empty_int
from app.schemas.users_schemas import UserRole
from app.schemas.lookup_enums import ManualLookupsStatus, ParsedLookupsStatus

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Index




class ManualLookups(Base):

    __tablename__ = "manual_lookups"

    id: Mapped[idpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), index=True)
    status: Mapped[non_empty_str] = mapped_column(default=ManualLookupsStatus.pending)
    brand: Mapped[non_empty_str] = mapped_column(index=True)
    model: Mapped[non_empty_str] = mapped_column(index=True)
    year: Mapped[non_empty_int]
    mileage_km: Mapped[non_empty_int] 
    fuel_category: Mapped[non_empty_str]
    transmission: Mapped[non_empty_str]
    power_kw: Mapped[non_empty_int]
    body_type: Mapped[non_empty_str]
    drive_train: Mapped[non_empty_str]
    condition: Mapped[non_empty_str]
    had_accident: Mapped[bool]
    has_full_service_history: Mapped[bool]
    previous_owners_qty: Mapped[int] = mapped_column(nullable=True)
    seller_is_dealer: Mapped[bool]
    price_listed: Mapped[int] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    
    
    __table_args__ = (
        Index("manual_brand_model_idx", "brand", "model"),
    )

    user: Mapped['Users'] = relationship(back_populates="manual_lookups")


class ParsedLookups(Base):

    __tablename__ = "parsed_lookups"

    id: Mapped[idpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), index=True)
    status: Mapped[non_empty_str] = mapped_column(default=ParsedLookupsStatus.parsed)
    url: Mapped[non_empty_str] 
    brand: Mapped[str] = mapped_column(nullable=True, default=None, index=True)
    model: Mapped[str] = mapped_column(index=True)
    year: Mapped[int] = mapped_column(default=None, nullable=True)
    mileage_km: Mapped[int] = mapped_column(default=None, nullable=True)
    fuel_category: Mapped[str] = mapped_column(default=None, nullable=True)
    transmission: Mapped[str] = mapped_column(default=None, nullable=True)
    power_kw: Mapped[int] = mapped_column(default=None, nullable=True)
    body_type: Mapped[str] = mapped_column(default=None, nullable=True)
    drive_train: Mapped[str] = mapped_column(default=None, nullable=True)
    condition: Mapped[str] = mapped_column(default=None, nullable=True)
    had_accident: Mapped[bool] = mapped_column(default=None, nullable=True)
    has_full_service_history: Mapped[bool] = mapped_column(default=None, nullable=True)
    previous_owners_qty: Mapped[int] = mapped_column(nullable=True, default=1)
    seller_is_dealer: Mapped[bool] = mapped_column(default=None, nullable=True)
    price_listed: Mapped[int] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    
    __table_args__ = (
        Index("parsed_brand_model_idx", "brand", "model"),
    )

    user: Mapped['Users'] = relationship(back_populates="parsed_lookups")


class ParsedLookupsRawData(Base):

    __tablename__ = 'parsed_raw_data'

    id: Mapped[idpk]
    parsed_lookup_id: Mapped[int] = mapped_column(ForeignKey("parsed_lookups.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    raw_data: Mapped[str]