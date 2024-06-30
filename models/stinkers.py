from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

FANTASY_TEAMS = ['Matt', 'Stephen', 'Kyle', 'Tyler', 'Andrew', 'Evan']

class Week(str, Enum):
    WEEK_1 = 'Week 1 - 8/29-9/2'
    WEEK_2 = 'Week 2 - 9/6-9/7'
    WEEK_3 = 'Week 3 - 9/12-9/14'
    WEEK_4 = 'Week 4 - 9/19-9/21'
    WEEK_5 = 'Week 5 - 9/26-9/28'
    WEEK_6 = 'Week 6 - 10/3-10/5'
    WEEK_7 = 'Week 7 - 10/9-10/12'
    WEEK_8 = 'Week 8 - 10/15-10/19'
    WEEK_9 = 'Week 9 - 10/22-10/26'
    WEEK_10 = 'Week 10 - 10/29-11/2'
    WEEK_11 = 'Week 11 - 11/5-11/9'
    WEEK_12 = 'Week 12 - 11/12-11/16'
    WEEK_13 = 'Week 13 - 11/19-11/23'
    WEEK_14 = 'Week 14 - 11/26-11/30'

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