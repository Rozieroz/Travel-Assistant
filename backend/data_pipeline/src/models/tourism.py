from pydantic import BaseModel
from typing import List, Optional

class EntryFee(BaseModel):
    citizen: str
    resident: str
    non_resident: str

class TourismLocation(BaseModel):
    name: str
    url: str
    type: str
    climate: Optional[str] = "Tropical"
    activities: List[str] = []
    description: Optional[str] = ""
    fees: Optional[EntryFee] = None