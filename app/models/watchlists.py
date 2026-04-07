from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str, non_empty_int

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Index


class Watchlist(Base):

    __tablename__ = "watchlist"

    id: Mapped[idpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False, index=True)
    url: Mapped[non_empty_str]
    last_price: Mapped[non_empty_int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    __table_args__ = (
        Index("users_urls", "user_id", "url"),
    )



class PriceAlerts(Base):

    __tablename__ = "price_alerts"

    id: Mapped[idpk]
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlist.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False, index=True)
    price_diff: Mapped[non_empty_int]
    price_diff_percents: Mapped[non_empty_int]
    is_sent: Mapped[bool] = mapped_column(default=False)
    noticed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))