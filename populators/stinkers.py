from typing import List
from models.stinkers import GameInfo, Stinker, StinkerInfo, MessageInfo, StinkerWeek

def create_game_info(game_id: int, 
                     game_complete: bool,
                     home_team: str, 
                     home_score: int, 
                     away_team: str, 
                     away_score: int, 
                     kickoff: str) -> GameInfo:
    return GameInfo(game_id=game_id, 
                    game_complete=game_complete,
                    home_team=home_team, 
                    home_score=home_score, 
                    away_team=away_team, 
                    away_score=away_score, 
                    kickoff=kickoff)

def create_stinker(team: str, 
                   record: str) -> Stinker:
    return Stinker(team=team, 
                   record=record)

def create_stinker_info(fantasy_team: str, 
                        stinker: Stinker, 
                        game_info: GameInfo, 
                        text_line: str) -> StinkerInfo:
    return StinkerInfo(fantasy_team=fantasy_team, 
                       stinker=stinker, 
                       game_info=game_info, 
                       text_line=text_line)

def create_message_info(send_message: bool, 
                        body: str) -> MessageInfo:
    return MessageInfo(send_message=send_message, 
                       body=body)

def create_stinker_week(week: int,
                        date: str, 
                        stinkers: List[StinkerInfo], 
                        message_info: MessageInfo) -> StinkerWeek:
    return StinkerWeek(week=week,
                       date=date, 
                       stinkers=stinkers, 
                       message_info=message_info)