from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str, non_empty_int
from app.schemas.users_schemas import UserRole
from app.schemas.payment_schemas import PaymentStatus

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey


class Users(Base):

    __tablename__ = "users"

    id: Mapped[idpk]
    full_name: Mapped[non_empty_str] = mapped_column(index=True)
    email: Mapped[non_empty_str] = mapped_column(unique=True, index=True)
    current_balance: Mapped[int] = mapped_column(nullable=True, default=4)
    hashed_password: Mapped[non_empty_str]
    role: Mapped[non_empty_str] = mapped_column(default=UserRole.user)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    deleted_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    manual_lookups: Mapped["ManualLookups"] = relationship(back_populates="user")
    parsed_lookups: Mapped["ParsedLookups"] = relationship(back_populates="user")
    payments: Mapped["Payments"] = relationship(back_populates="user")

class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[idpk]
    user_id: Mapped[non_empty_int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    rate: Mapped[non_empty_str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    status: Mapped[non_empty_str] = mapped_column(server_default=PaymentStatus.pending)

    user: Mapped["Users"] = relationship(back_populates="payments")