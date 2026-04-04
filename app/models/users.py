from datetime import datetime, timezone

from app.models.base import Base, idpk, non_empty_str
from app.schemas.users_schemas import UserRole

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime


class Users(Base):

    __tablename__ = "users"

    id: Mapped[idpk]
    full_name: Mapped[non_empty_str] = mapped_column(index=True)
    email: Mapped[non_empty_str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[non_empty_str]
    role: Mapped[non_empty_str] = mapped_column(default=UserRole.user)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc))
    deleted_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    manual_lookups: Mapped["ManualLookups"] = relationship(back_populates="user")
    parsed_lookups: Mapped["ParsedLookups"] = relationship(back_populates="user")