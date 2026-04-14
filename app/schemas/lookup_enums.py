from enum import Enum

class ManualLookupsMode(str, Enum):
    seller = "seller"
    buyer = "buyer"

class ManualLookupsStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    gemini_failed = "gemini_failed"

class ParsedLookupsStatus(str, Enum):
    parsed = "parsed"
    pending = "pending"
    completed = "completed"
    failed = "failed"
    gemini_failed = "gemini_failed"


class FuelCategories(str, Enum):
    gasoline = "gasoline"
    electric_gasoline = "electric/gasoline"
    electric_diesel = "electric/diesel"
    electric = "electric"
    diesel = "diesel"
    cng = 'cng'
    ethanol = "ethanol"
    lpg = "lpg"
    others = "others"

class Condition(str, Enum):
    used = "used"
    new = "new"

class TransmissionType(str, Enum):
    automathic = "automathic"
    semi_automathic = "semi_automathic"
    manual = "manual"

class BodyTypes(str, Enum):
    offroad_pickup = "off-road/pick-up" 
    station_wagon = "station wagon"
    coupe = "coupe"
    sedan = "sedan"
    convertible = "convertible"
    compact = "compact"
    van = "van"
    other = "other"
    transporter = "transporter"


class DriveTrainTypes(str, Enum):
    full_4wd = "4wd"
    unknown = "unknown"
    front = "front wheel drive"
    rear = "rear wheel drive"


class BoolType(int, Enum):
    true = 1
    false = 0