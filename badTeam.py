import pandas as pd
from time import sleep
import cfbd
from datetime import datetime, date
import random
from tqdm import tqdm
import os
from dotenv import load_dotenv
from utils import TwilioTexter
from constants import ESPN_FPI_URL, CFB_REFERENCE_NAME_EXCEPTIONS, ACCEPTABLE_CONFERENCES, FANTASY_TEAMS, TWILIO_NUMBER

load_dotenv()

CFBD_API_KEY = os.getenv('CFBD_API_KEY')

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

# Read in FPI data
fpi_rnk_df = pd.read_html(ESPN_FPI_URL)[0]

twilio_texter = TwilioTexter()

def get_date(date_str):
    return pd.to_datetime(date_str).date()


def get_conference_teams(ACCEPTABLE_CONFERENCES=ACCEPTABLE_CONFERENCES, EXCEPTIONS=CFB_REFERENCE_NAME_EXCEPTIONS):
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
    teams = api_instance.get_fbs_teams(year=datetime.today().year)

    valid_teams = []
    for team in teams:
        team_name = team.school
        team_conference = team.conference
        
        if team_conference in ACCEPTABLE_CONFERENCES:
            valid_teams.append(team_name)

    return valid_teams


def get_team_schedule(team_name, date):
    todays_date = date

    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    team_schedule = api_instance.get_games(year=todays_date.year, team=team_name)

    return team_schedule


def get_next_game(team_name, date):
    todays_date = get_date(date)

    team_schedule = get_team_schedule(team_name, todays_date)

    game_dates = [get_date(game.start_date) for game in team_schedule]
    next_game_date = min(filter(lambda x: x >= todays_date, game_dates))

    # get first (and only) element from iterator
    next_game = list(filter(lambda x: get_date(x.start_date) == next_game_date, team_schedule))
    if len(next_game) == 0:
        print(f'Could not find next game for {team_name}')
        next_game = None
    else:
        next_game = next_game[0]
    return next_game


def team_has_game_this_week(team_name, date):
    todays_date = get_date(date)

    team_next_game = get_next_game(team_name, todays_date)

    team_next_game_date = get_date(team_next_game.start_date)
    return (team_next_game_date - todays_date).days <= 5  # set at 5 to allow for weird day of week games 


def get_team_fpi_rating(team_name):
    api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))
    api_response = api_instance.get_fpi_ratings(year='2024', team=team_name)
    if (api_response is None) or (len(api_response) == 0):
        api_response = api_instance.get_fpi_ratings(year='2023', team=team_name)
    try:
        fpi = api_response[0].fpi
        return fpi
    except:
        print(f'Cannot find FPI for {team_name}')


def get_team_record(team_name):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    record = api_instance.get_team_records(year=2024, team=team_name)
    if (record is None) or (len(record) == 0):
        record = api_instance.get_team_records(year=2023, team=team_name)
    try:
        total_record = record[0].total
        record_str = f'{total_record.wins}-{total_record.losses}'
    except:
        record_str = ''
    return record_str


def get_bottom_n_teams(fpi_dict, bottom_n):
    sorted_dict = dict(sorted(fpi_dict.items(), key=lambda item: item[1]))
    return list(sorted_dict.keys())[0:bottom_n]


def format_game_info_for_text(fantasy_team, team, game, team_record):
    team_info = f'{team} ({team_record})'

    is_home = game.home_team == team
    opponent_info = game.away_team if is_home else game.home_team
    body = f'{team_info}, {"home vs" if is_home else "playing @"} {opponent_info}'

    message = f'{fantasy_team} has {body}'
    return message

def format_date(week_str):
    parts = week_str.split("-")
    extracted_date = parts[1].strip()
    return extracted_date + "/2024"

def main(target_date, send_text, fantasy_teams):
    # Parse date from enum string
    target_date = format_date(target_date)

    # Retrieve valid teams within our acceptable conferences
    all_teams = get_conference_teams()
    print('Got teams.')

    # Building map of {team -> FPI Ranking} for those teams that have a game in the upcoming week
    print('Getting schedules.')
    keep_teams_fpi = {}
    for team in tqdm(all_teams):
        sleep(0.5)
        try:
            if team_has_game_this_week(team, target_date):
                keep_teams_fpi[team] = get_team_fpi_rating(team)
        except:
            print("Couldn't get schedule for: {}".format(team))
        
    print('Finished cfb data part!')

    # Extract the worst N teams from our map
    bottom_teams = get_bottom_n_teams(keep_teams_fpi, len(fantasy_teams))

    # Shuffle each list
    random.shuffle(fantasy_teams)
    random.shuffle(bottom_teams)

    # Create a tuple for each fantasy team and the team they will be assigned
    pairs = {}
    for team, fantasy_team in zip(bottom_teams, fantasy_teams):
        pairs[fantasy_team] = team

    text_lines = []
    for fantasy_team, team in pairs.items():
        next_game = get_next_game(team, target_date)
        team_record = get_team_record(team)

        text_body = format_game_info_for_text(fantasy_team, team, next_game, team_record)
        text_lines.append(text_body)

    full_text_body = '\n'.join(text_lines)

    print('Full text body: ', full_text_body)

    if send_text:
        print('Sending text!')
        twilio_texter.send_text(to_number=TWILIO_NUMBER, body=full_text_body)

    return full_text_body

if __name__ == '__main__':
    main()