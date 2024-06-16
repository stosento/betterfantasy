import pandas as pd
import os
import random
import cfbd
import time
# from discordBot import send_message
from time import sleep
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv
from utils import TwilioTexter

from constants import ESPN_FPI_URL, CFB_REFERENCE_NAME_EXCEPTIONS, ACCEPTABLE_CONFERENCES
from populators.stinkers import (
    create_game_info,
    create_stinker,
    create_stinker_info,
    create_text_info,
    create_stinker_week
)

load_dotenv()

CFBD_API_KEY = os.getenv('CFBD_API_KEY')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

# Read in FPI data
fpi_rnk_df = pd.read_html(ESPN_FPI_URL)[0]

twilio_texter = TwilioTexter()

def get_date(date_str):
    return pd.to_datetime(date_str).date()

def get_fpi_ratings_map():
    api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))
    api_response = api_instance.get_fpi_ratings(year='2024')
    if (api_response is None) or (len(api_response) == 0):
        api_response = api_instance.get_fpi_ratings(year='2023')
    fpi_dict = {}
    for team in api_response:
        # Only add to dict if part of our conferences
        if team.conference in ACCEPTABLE_CONFERENCES:
            fpi_dict[team.team] = team.fpi
    return fpi_dict

def get_next_week_games(week):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    games = api_instance.get_games(year=2024, week=week, season_type='regular')
    return games

def filter_games_by_conferences(games, conference):
    result = {}
    for game in games:
        if game.home_conference in conference:
            result[game.home_team] = game
        if game.away_conference in conference:
            result[game.away_team] = game
    return result

def get_records_dict():
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    records = api_instance.get_team_records(year=2024)
    if (records is None) or (len(records) == 0):
        records = api_instance.get_team_records(year=2023)
    record_dict = {}
    for record in records:
        record_dict[record.team] = f'{record.total.wins}-{record.total.losses}'
    return record_dict

def get_bottom_n_teams(fpi_dict, bottom_n):
    sorted_dict = dict(sorted(fpi_dict.items(), key=lambda item: item[1]))
    return list(sorted_dict.keys())[0:bottom_n]

def build_message(fantasy_team, team, game, team_record):
    team_info = f'{team} ({team_record})'

    is_home = game.home_team == team
    opponent_info = game.away_team if is_home else game.home_team
    body = f'{team_info}, {"home vs" if is_home else "playing @"} {opponent_info}'
    message = f'{fantasy_team} has {body}'

    return message

def build_stinker_info(fantasy_team, team, game, team_record):
    message = build_message(fantasy_team, team, game, team_record)

    stinker = create_stinker(team=team, record=team_record)
    game_info = create_game_info(home_team=game.home_team, away_team=game.away_team, kickoff=game.start_date)
    stinker_info = create_stinker_info(fantasy_team=fantasy_team, stinker=stinker, game_info=game_info, text_line=message)
    
    return stinker_info

def format_date(week_str):
    parts = week_str.split("-")
    extracted_date = parts[1].strip()
    return extracted_date + "/2024"

def extract_week(week_str):
    return int(week_str.split("-")[0].split(" ")[1].strip())

def get_bottom_games(teams, games):
    return {team: games[team] for team in teams if team in games}

async def main(target_date, send_text, fantasy_teams):
    start_time = time.time() 

    week = extract_week(target_date)

    # Parse date from enum string
    target_date = format_date(target_date)

    # Build the next week's games we care about
    next_week_games = get_next_week_games(week)
    next_week_relevant_games_map = filter_games_by_conferences(next_week_games, ACCEPTABLE_CONFERENCES)

    # Get FPI Ratings Map
    fpi_ratings_map = get_fpi_ratings_map()

    # Limit our map to those that are in the next week relevant games
    fpi_ratings_map = {k: v for k, v in fpi_ratings_map.items() if k in next_week_relevant_games_map.keys()}

    # Sort the map by FPI rating, lowest to highest
    fpi_ratings_map = dict(sorted(fpi_ratings_map.items(), key=lambda item: item[1]))

    # Extract the worst N teams from our map & get the game details for each
    bottom_teams = list(fpi_ratings_map.keys())[0:len(fantasy_teams)]
    bottom_games = get_bottom_games(bottom_teams, next_week_relevant_games_map)

    # Build the record map for the bottom teams
    records_dict = get_records_dict()

    # Shuffle the fantasy teams, games and match them
    random.shuffle(fantasy_teams)
    random.shuffle(bottom_teams)

    pairs = {}
    for team, fantasy_team in zip(bottom_teams, fantasy_teams):
        pairs[fantasy_team] = team

    # Convert the game details into a list of stinker info objects
    stinker_info_list = []
    for fantasy_team, team in pairs.items():
        next_game = bottom_games[team]
        team_record = records_dict[team]

        stinker_info = build_stinker_info(fantasy_team, team, next_game, team_record)
        stinker_info_list.append(stinker_info)

    # Build the response object
    full_text_body = "\n".join([stinker_info.text_line for stinker_info in stinker_info_list])
    print('Full text body: ', full_text_body)

    # TODO - Replace Text with Discord
    # https://discordpy.readthedocs.io/en/latest/quickstart.html

    if send_text:
        print('Sending message!')
        # await send_message(full_text_body)
        # twilio_texter.send_text(to_number=TWILIO_NUMBER, body=full_text_body)

    text_info = create_text_info(sent=send_text, to=TWILIO_NUMBER, body=full_text_body)
    stinker_week = create_stinker_week(date=target_date, stinkers=stinker_info_list, text_info=text_info)

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print(f"Execution time: {elapsed_time} seconds")

    return stinker_week

if __name__ == '__main__':
    main()