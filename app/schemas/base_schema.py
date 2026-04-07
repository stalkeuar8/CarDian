from pydantic import BaseModel
from typing import Sequence


class BaseSchema(BaseModel):
    pass

class SequenceBaseSchema(BaseModel):
    items: Sequence[BaseSchema]