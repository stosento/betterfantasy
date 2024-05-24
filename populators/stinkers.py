from typing import List
from models.stinkers import GameInfo, Stinker, StinkerInfo, TextInfo, StinkerWeek

def create_game_info(home_team: str, away_team: str, kickoff: str, spread: str) -> GameInfo:
    return GameInfo(home_team=home_team, away_team=away_team, kickoff=kickoff, spread=spread)

def create_stinker(team: str, record: str) -> Stinker:
    return Stinker(team=team, record=record)

def create_stinker_info(fantasy_team: str, stinker: Stinker, game_info: GameInfo) -> StinkerInfo:
    return StinkerInfo(fantasy_team=fantasy_team, stinker=stinker, game_info=game_info)

def create_text_info(sent: bool, to: str, body: str) -> TextInfo:
    return TextInfo(sent=sent, to=to, body=body)

def create_stinker_week(date: str, stinkers: List[StinkerInfo], text_info: TextInfo) -> StinkerWeek:
    return StinkerWeek(date=date, stinkers=stinkers, text_info=text_info)