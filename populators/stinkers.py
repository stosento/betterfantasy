from typing import List
from models.stinkers import GameInfo, Stinker, StinkerInfo, MessageInfo, StinkerWeek

def create_game_info(home_team: str, away_team: str, kickoff: str) -> GameInfo:
    return GameInfo(home_team=home_team, away_team=away_team, kickoff=kickoff)

def create_stinker(team: str, record: str) -> Stinker:
    return Stinker(team=team, record=record)

def create_stinker_info(fantasy_team: str, stinker: Stinker, game_info: GameInfo, text_line: str) -> StinkerInfo:
    return StinkerInfo(fantasy_team=fantasy_team, stinker=stinker, game_info=game_info, text_line=text_line)

def create_message_info(send_requested: bool, body: str) -> MessageInfo:
    return MessageInfo(send_requested=send_requested, body=body)

def create_stinker_week(date: str, stinkers: List[StinkerInfo], message_info: MessageInfo) -> StinkerWeek:
    return StinkerWeek(date=date, stinkers=stinkers, message_info=message_info)