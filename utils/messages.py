from models.stinkers import StinkerWeek, GameStatus

def build_stinker_assignments_message(stinker_week:StinkerWeek):
    message_body = "\n".join([stinker.text_line for stinker in stinker_week.stinkers])
    return message_body

def build_stinker_results_message(stinker_week:StinkerWeek):
    messages = []

    for item in stinker_week.stinkers:
        assigned_team = item.stinker.team
        game = item.game_info
        game_status = game.game_status

        assigned_score = game.home_score if assigned_team == game.home_team else game.away_score
        opponent_score = game.away_score if assigned_team == game.home_team else game.home_score

        line1 = f"{item.fantasy_team}'s Stinker -- {assigned_team} ({item.stinker.record}) \n"
        line2 = f"Game Status: {game_status}\n"

        if game_status == GameStatus.NOT_STARTED:
            line2 = f"Game Status: {game_status} -- {game.kickoff}\n"

        line3 = f"{game.home_team} {game.home_score} - {game.away_team} {game.away_score}\n"

        stinker_message = line1 + line2 + line3
        
        if game_status == GameStatus.COMPLETE:
            if assigned_score > opponent_score:
                line4 = f"{assigned_team} WINS!!\n"
                stinker_message += line4

        messages.append(stinker_message)

    message_body = "\n".join([message for message in messages])
    return message_body