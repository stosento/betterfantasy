from array import array
from models.db_models import Stinker as DBStinker, Week as DBWeek
from models.stinkers import StinkerInfo, StinkerWeek, GameInfo, Stinker, MessageInfo

def create_db_stinker(week_number: int, stinker: StinkerInfo):
    return DBStinker(
        week_number=week_number,
        fantasy_team=stinker.fantasy_team,
        stinker_team=stinker.stinker.team,
        stinker_record=stinker.stinker.record,
        game_id=stinker.game_info.game_id,
        game_complete=stinker.game_info.game_complete,
        home_team=stinker.game_info.home_team,
        home_score=stinker.game_info.home_score,
        away_team=stinker.game_info.away_team,
        away_score=stinker.game_info.away_score,
        kickoff=stinker.game_info.kickoff,
        text_line=stinker.text_line
    )

def create_stinker_week_from_db(db_week: DBWeek, db_stinkers: array):
    return StinkerWeek(
        week=db_week.week_number,
        date=db_week.date,
        stinkers=[
            StinkerInfo(
                fantasy_team=stinker.fantasy_team,
                stinker=Stinker(team=stinker.stinker_team, record=stinker.stinker_record),
                game_info=GameInfo(
                    game_id=stinker.game_id,
                    game_complete=stinker.game_complete,
                    home_team=stinker.home_team,
                    home_score=stinker.home_score,
                    away_team=stinker.away_team,
                    away_score=stinker.away_score,
                    kickoff=stinker.kickoff
                ),
                text_line=stinker.text_line
            ) for stinker in db_stinkers
        ],
        message_info=MessageInfo(
            send_message=False,
            body="\n".join([stinker.text_line for stinker in db_stinkers])
        )
    )