import pandas as pd
from time import sleep
import cfbd
from datetime import datetime
import random
from tqdm import tqdm
from utils import TwilioTexter
from constants import ESPN_FPI_URL, CFB_REFERENCE_NAME_EXCEPTIONS, ACCEPTABLE_CONFERENCES, FANTASY_TEAMS, CFBD_API_KEY

# Configure API key authorization: ApiKeyAuth
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = CFBD_API_KEY
configuration.api_key_prefix['Authorization'] = 'Bearer'

fpi_rnk_df = pd.read_html(ESPN_FPI_URL)[0]

BOTTOM_N = len(FANTASY_TEAMS)
twilio_texter = TwilioTexter()

def get_date(date_str):
    return pd.to_datetime(date_str).date()


def get_conference_teams(ACCEPTABLE_CONFERENCES=ACCEPTABLE_CONFERENCES, EXCEPTIONS=CFB_REFERENCE_NAME_EXCEPTIONS):
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
    teams = api_instance.get_fbs_teams(year=datetime.today().year)

    keep_teams = []
    for team in teams:
        team_name = team.school
        team_conference = team.conference
        
        if team_conference in ACCEPTABLE_CONFERENCES:
            keep_teams.append(team_name)

    return keep_teams


def get_team_schedule(team_name):
    todays_date = datetime.today().date()
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    team_schedule = api_instance.get_games(year=todays_date.year, team=team_name)
    return team_schedule


def get_next_game(team_name):
    todays_date = datetime.today().date()
    team_schedule = get_team_schedule(team_name)

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


def team_has_game_this_week(team_name):
    todays_date = datetime.today().date()
    team_next_game = get_next_game(team_name)
    team_next_game_date = get_date(team_next_game.start_date)
    return (team_next_game_date - todays_date).days <= 5  # set at 5 to allow for weird day of week games 


def get_team_fpi_rating(team_name):
    api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))
    api_response = api_instance.get_fpi_ratings(year=datetime.today().year, team=team_name)
    try:
        fpi = api_response[0].fpi
        return fpi
    except:
        print(f'Cannot find FPI for {team_name}')


def get_team_record(team_name):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    record = api_instance.get_team_records(year=datetime.today().year, team=team_name)
    try:
        total_record = record[0].total
        record_str = f'{total_record.wins}-{total_record.losses}'
    except:
        record_str = ''
    return record_str


def get_bottom_n_teams(fpi_dict, bottom_n=len(FANTASY_TEAMS)):
    worst_n_scores = []
    for k, v in fpi_dict.items():
        if len(worst_n_scores) < bottom_n:
            worst_n_scores.append(v)
        else:
            if v < max(worst_n_scores):
                worst_n_scores.remove(max(worst_n_scores))
                worst_n_scores.append(v)
    
    worst_teams = [k for k, v in fpi_dict.items() if v in worst_n_scores]
    return worst_teams[0:bottom_n]


def format_game_info_for_text(fantasy_team, team, game, team_record):
    team_info = f'{team} ({team_record})'

    is_home = game.home_team == team

    if is_home:
        opponent_info = game.away_team
    else:
        opponent_info = game.home_team

    if not is_home:
        body = f'{team_info}, playing @ {opponent_info}'
    else:
        body = f'{team_info}, home vs {opponent_info}'

    message = f'{fantasy_team} has {body}'
    return message



all_teams = get_conference_teams()
print('Got teams.')

print('Getting schedules.')
keep_teams_fpi = {}
for team in tqdm(all_teams):
    sleep(0.5)
    try:
        has_game = team_has_game_this_week(team)
        if has_game:
            api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))

            keep_teams_fpi[team] = get_team_fpi_rating(team)
    except:
        print("Couldn't get schedule for: {}".format(team))
    
print('Finished cfb data part!')

bottom_teams = get_bottom_n_teams(keep_teams_fpi)

random.shuffle(FANTASY_TEAMS)
random.shuffle(bottom_teams)

pairs = {}
for team, fantasy_team in zip(bottom_teams, FANTASY_TEAMS):
    pairs[fantasy_team] = team

text_lines = []
for fantasy_team, team in pairs.items():
    next_game = get_next_game(team)
    team_record = get_team_record(team)

    text_body = format_game_info_for_text(fantasy_team, team, next_game, team_record)
    text_lines.append(text_body)

full_text_body = '\n'.join(text_lines)

print(full_text_body)

twilio_texter.send_text(to_number='+17346523203', body=full_text_body)