import datetime
from datetime import datetime
from models.db_models import GameStatus as DBGameStatus
import pytz

def is_past_kickoff(kickoff):
    try:
        # Parse the kickoff string
        kickoff_datetime = datetime.strptime(kickoff, "%A @ %I:%M%p EST (%m/%d/%Y)")

        # Set the time zone to EST
        est = pytz.timezone('US/Eastern')
        kickoff_datetime = est.localize(kickoff_datetime)

        # Get current time in EST
        current_time = datetime.now(est)

        # Compare kickoff time with current time
        return current_time > kickoff_datetime

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in is_past_kickoff: {e}")
        print(f"Problematic kickoff string: {kickoff}")

        # Return False if there's any issue
        return False

def build_game_status(game):

    print('game in build_game_status', game)
    status = DBGameStatus.NOT_STARTED

    if game.completed:
        status = DBGameStatus.COMPLETE
    elif is_past_kickoff(game.kickoff):
        status = DBGameStatus.IN_PROGRESS

    return status
