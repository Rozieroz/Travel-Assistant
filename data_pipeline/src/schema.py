"""
Pydantic models for the tourism data schema.
Validates structure and types.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class Activity(BaseModel):
    name: str
    type: str = Field(..., pattern="^(adventure|relaxation|wildlife|cultural)$")
    estimated_cost: str  # Could be "Free", "500-1000 KES", etc.

class EntryFee(BaseModel):
    citizen: str
    resident: str
    non_resident: str

class DailyCost(BaseModel):
    budget: str
    mid: str
    luxury: str

class TransportOption(BaseModel):
    type: str = Field(..., pattern="^(road|air|train)$")
    estimated_cost: str

class TourismLocation(BaseModel):
    id: str                     # Unique slug (e.g., "amboseli-national-park")
    name: str
    type: str = Field(..., pattern="^(city|park|beach|mountain|forest)$")
    county: str
    region: str                 # e.g., "Rift Valley", "Coast"
    description: str
    climate: str                # Short climate description
    best_time: str              # e.g., "June-October"
    activities: List[Activity]
    entry_fee: EntryFee
    estimated_daily_cost: DailyCost
    transport_options: List[TransportOption]
    nearby_locations: List[str] # Names of nearby places
    tags: List[str]             # e.g., ["big five", "hiking", "beach"]