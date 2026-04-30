from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated

idpk = Annotated[int, mapped_column(primary_key=True)]
non_empty_str = Annotated[str, mapped_column(nullable=False)]
non_empty_int = Annotated[int, mapped_column(nullable=False)]


class Base(DeclarativeBase):
    pass