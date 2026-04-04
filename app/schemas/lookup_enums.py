from enum import Enum

class ManualLookupsMode(str, Enum):
    seller = "seller"
    buyer = "buyer"

class ParsedLookupsStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class FuelType(str, Enum):
    gasoline = "gasoline"
    hybrid = "hybrid"
    diesel = "diesel"
    flex_fuel = "flex_fuel"

class TransmissionType(str, Enum):
    auto = "auto"
    cvt = "cvt"
    manual = "manual"
    other = "other"