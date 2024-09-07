from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

from constants import FANTASY_TEAMS
from models.common import Week


# ------------------- STINKER REQUEST / RESPONSE -------------------

class StinkersRequest(BaseModel):
    teams: List[str] = Field(default=FANTASY_TEAMS, description="List of fantasy team names")

    class Config:
        schema_extra = {
            "example": {
                "teams": FANTASY_TEAMS
            }
        }

class StinkersResultsRequest(BaseModel):
    week: Week = Field(..., description="Week for which to get stinker results")
    send_message: bool = Field(False, description="Whether to send a message with the results")

# ------------------- STINKER OBJECTS -------------------

class GameStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"

class GameInfo(BaseModel):
    game_id: int
    game_status: GameStatus = GameStatus.NOT_STARTED
    home_team: str
    home_score: int
    away_team: str
    away_score: int
    kickoff: str

class Stinker(BaseModel):
    team: str
    record: str

class StinkerInfo(BaseModel):
    fantasy_team: str
    stinker: Stinker
    game_info: GameInfo
    text_line: str

class MessageInfo(BaseModel):
    send_message: bool
    body: str

class StinkerWeek(BaseModel):
    week: int
    date: str
    stinkers: List[StinkerInfo]
    message_info: MessageInfo
