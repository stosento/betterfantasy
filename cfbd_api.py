import os
import cfbd
from dotenv import load_dotenv

from constants import ACCEPTABLE_CONFERENCES

load_dotenv()

CFBD_API_KEY = os.getenv('CFBD_API_KEY')
CURRENT_YEAR = os.getenv('CURRENT_YEAR')
PAST_YEAR = os.getenv('PAST_YEAR')

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

def get_fpi_ratings_map(next_week_games_map):
    api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))
    api_response = api_instance.get_fpi_ratings(year=CURRENT_YEAR)
    if (api_response is None) or (len(api_response) == 0):
        api_response = api_instance.get_fpi_ratings(year=PAST_YEAR)
    fpi_dict = {}
    for team in api_response:
        # Only add to dict if part of our conferences
        if team.conference in ACCEPTABLE_CONFERENCES:
            fpi_dict[team.team] = team.fpi

    # Restrict to games in the next week
    fpi_dict = {k: v for k, v in fpi_dict.items() if k in next_week_games_map.keys()}

    # Sort the map by FPI rating, lowest to highest
    fpi_dict = dict(sorted(fpi_dict.items(), key=lambda item: item[1]))

    return fpi_dict

def get_next_week_games(week):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    games = api_instance.get_games(year=int(CURRENT_YEAR), week=week, season_type='regular')
    return games

def get_records_dict():
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    records = api_instance.get_team_records(year=int(CURRENT_YEAR))
    if (records is None) or (len(records) == 0):
        records = api_instance.get_team_records(year=int(PAST_YEAR))
    record_dict = {}
    for record in records:
        record_dict[record.team] = f'{record.total.wins}-{record.total.losses}'
    return record_dict

def get_game_by_id(game_id):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    game = api_instance.get_games(year=int(CURRENT_YEAR), id=game_id)
    return game[0]
