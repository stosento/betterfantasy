import datetime
from datetime import datetime
from dateutil import parser
from models.db_models import GameStatus as DBGameStatus
import pytz

def is_past_kickoff(kickoff):
    try:
        # Parse the kickoff string
        kickoff_datetime = parser.isoparse(kickoff)

        # Ensure the kickoff time is timezone-aware (UTC)
        if kickoff_datetime.tzinfo is None:
            kickoff_datetime = pytz.utc.localize(kickoff_datetime)

        # Get current time in UTC
        current_time = datetime.now(pytz.utc)

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
    elif is_past_kickoff(game.start_date):
        status = DBGameStatus.IN_PROGRESS

    return status
