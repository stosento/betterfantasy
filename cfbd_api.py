import os
import cfbd
from dotenv import load_dotenv
from pprint import pprint

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

def get_defensive_weekly_stats(week_number):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    conference_abbreviation = "B1G"
    season_type = "regular"
    category = "defensive"
    stats = api_instance.get_player_game_stats(
        year=int(CURRENT_YEAR),
        week=week_number,
        season_type=season_type,
        conference=conference_abbreviation,
        category=category
    )
    return stats

def get_scoreboard():
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    games = api_instance.get_scoreboard()
    return games

def get_betting_lines(team, week):
    api_instance = cfbd.BettingApi(cfbd.ApiClient(configuration))
    betting = api_instance.get_lines(year=int(CURRENT_YEAR), week=week, team=team)

    if betting and betting[0].lines:
        first_line = betting[0].lines[0]
        formatted_spread = first_line.formatted_spread
        return formatted_spread
    else:
        return None