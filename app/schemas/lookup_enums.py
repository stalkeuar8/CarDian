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
    electric_gasoline = "electric_gasoline"
    electric_diesel = "electric_diesel"
    electric = "electric"
    diesel = "diesel"


class TransmissionType(str, Enum):
    automathic = "automathic"
    semi_automathic = "semi_automathic"
    manual = "manual"
    other = "other"