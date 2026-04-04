from datetime import timezone, datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import DateTime
from typing import Annotated

idpk = Annotated[int, mapped_column(primary_key=True)]
non_empty_str = Annotated[str, mapped_column(nullable=False)]
non_empty_int = Annotated[int, mapped_column(nullable=False)]


class Base(DeclarativeBase):
    pass