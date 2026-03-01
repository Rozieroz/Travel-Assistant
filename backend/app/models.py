from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    context_used: Optional[List[str]] = None
    weather_info: Optional[str] = None
    budget_info: Optional[str] = None

class BudgetRequest(BaseModel):
    location: str
    days: int
    budget_level: str = "mid"  # budget, mid, luxury

class BudgetResponse(BaseModel):
    total: str
    breakdown: str
    location: str

class WeatherRequest(BaseModel):
    location: str
    days_ahead: Optional[int] = 0

class WeatherResponse(BaseModel):
    summary: str