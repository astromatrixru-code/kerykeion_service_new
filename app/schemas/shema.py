from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChartType(str, Enum):
    NATAL = "Natal"
    TRANSIT = "Transit"
    SYNASTRY = "Synastry"

class Theme(str, Enum):
    LIGHT = "light"
    DARK = "dark"

class HouseSystem(str, Enum):
    PLACIDUS = "Placidus"
    KOCH = "Koch"
    WHOLE_SIGN = "Whole_Sign"
    EQUAL_HOUSE = "Equal_House"

# Natal chart request schema
class AstroRequest(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    city: str
    theme: Theme = Theme.LIGHT
    house_system: HouseSystem = HouseSystem.PLACIDUS

# Transit chart request schema    
class TransitRequest(BaseModel):
    person: AstroRequest
    transit_date: datetime = Field(default_factory=datetime.now)

# Synastry chart request schema    
class SynastryRequest(BaseModel):
    person_one: AstroRequest
    person_two: AstroRequest    
    
# Return chart request schema    
class ReturnRequest(BaseModel):
    person: AstroRequest
    return_year: int
    orbit_planet: str = "Sun"    
    