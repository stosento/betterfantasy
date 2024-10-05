from models.stinkers import StinkerWeek, GameStatus
from cfbd_api import get_scoreboard

def build_stinker_assignments_message(stinker_week:StinkerWeek):
    message_body = "\n".join([stinker.text_line for stinker in stinker_week.stinkers])
    return message_body

def build_stinker_results_message(stinker_week:StinkerWeek):
    messages = []

    scoreboard = get_scoreboard()

    for item in stinker_week.stinkers:
        assigned_team = item.stinker.team
        game = item.game_info
        game_status = game.game_status

        assigned_score = game.home_score if assigned_team == game.home_team else game.away_score
        opponent_score = game.away_score if assigned_team == game.home_team else game.home_score

        line1 = f"{item.fantasy_team}'s Stinker -- {assigned_team} ({item.stinker.record}) \n"
        line2 = f"{game.home_team} {game.home_score} - {game.away_team} {game.away_score}\n"
        line3 = f"{game.kickoff}\n"

        if game_status == GameStatus.IN_PROGRESS:
            game = get_game_from_scoreboard(game.id, scoreboard)
            period = game.period
            querter = ""
            if period == 1:
                quarter = "1st Quarter"
            elif period == 2:
                quarter = "2nd Quarter"
            elif period == 3:
                quarter = "3rd Quarter"
            elif period == 4:
                quarter = "4th Quarter"
            else:
                quarter = "Overtime"
            line3 = f"{game.clock} {quarter}\n"
        elif game_status == GameStatus.COMPLETE:
            line3 = "FINAL\n"

        stinker_message = line1 + line2 + line3
        
        if game_status == GameStatus.COMPLETE:
            if assigned_score > opponent_score:
                line4 = f"{assigned_team} WINS!!\n"
                stinker_message += line4

        messages.append(stinker_message)

    message_body = "\n".join([message for message in messages])
    return message_body

def get_game_from_scoreboard(game_id, scoreboard):
    for game in scoreboard:
        if game.id == game_id:
            return game

    return None