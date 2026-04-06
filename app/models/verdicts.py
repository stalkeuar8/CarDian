from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str, non_empty_int

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Index


class Verdicts(Base):

    __tablename__ = "verdicts"

    id: Mapped[idpk]
    manual_lookup_id: Mapped[int] = mapped_column(ForeignKey("manual_lookups.id", ondelete="RESTRICT", onupdate='RESTRICT'), nullable=True, default=None)
    parsed_lookup_id: Mapped[int] = mapped_column(ForeignKey("parsed_lookups.id", ondelete="RESTRICT", onupdate='RESTRICT'), nullable=True, default=None)
    predicted_price: Mapped[non_empty_int] = mapped_column(nullable=False)
    price_deviation_percent: Mapped[int] = mapped_column(nullable=True)
    verdict: Mapped[non_empty_str] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    