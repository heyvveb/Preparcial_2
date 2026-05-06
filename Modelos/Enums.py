from enum import Enum

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class main_statEnum(str,Enum):
    Strength = "Strength"
    Dexterity = "Dexterity"
    Quality = "Quality"
    Sorcerer = "Sorcerer"
    Faith = "Faith"
    Pyromancer = "Pyromancer"
    Tank = "Tank"
    Hybrid = "Hybrid"