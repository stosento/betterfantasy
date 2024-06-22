from typing import List
from pydantic import BaseModel

class GameInfo(BaseModel):
    game_id: int
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
    date: str
    stinkers: List[StinkerInfo]
    message_info: MessageInfo


