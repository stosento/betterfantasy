from pydantic import BaseModel, Field
from typing import List
from models.common import Week

class DefensiveStatsRequest(BaseModel):
    week: Week = Field(..., description="Week for which to get defensive stats")

class TackleStat(BaseModel):
    player: str
    tackles: int
class WeeklyTackleStats(BaseModel):
    week: int
    stats: List[TackleStat]
