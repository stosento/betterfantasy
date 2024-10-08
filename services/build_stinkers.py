import os
import random
import pytz
from datetime import datetime

from models.db_models import Stinker as DBStinker, GameStatus as DBGameStatus

from cfbd_api import get_fpi_ratings_map, get_next_week_games, get_records_dict, get_game_by_id, get_betting_lines
from constants import ACCEPTABLE_CONFERENCES
from populators.stinkers import (
    create_game_info,
    create_stinker,
    create_stinker_info,
    create_message_info,
    create_stinker_week
)

CURRENT_YEAR = os.getenv('CURRENT_YEAR')

def get_date(date_str):
    return pd.to_datetime(date_str).date()

def filter_games_by_conferences(games, conference):
    result = {}
    for game in games:
        if game.home_conference in conference:
            result[game.home_team] = game
        if game.away_conference in conference:
            result[game.away_team] = game
    return result

def get_bottom_n_teams(fpi_dict, bottom_n):
    sorted_dict = dict(sorted(fpi_dict.items(), key=lambda item: item[1]))
    return list(sorted_dict.keys())[0:bottom_n]

def build_message(fantasy_team, team, week, game, team_record, kickoff):
    team_info = f'{team} ({team_record})'

    # Make call to get betting line
    betting = get_betting_lines(team, week)

    is_home = game.home_team == team
    opponent_info = game.away_team if is_home else game.home_team
    body = f'{team_info}, {"home vs" if is_home else "playing @"} {opponent_info} -- [{betting}]'
    message = f'{fantasy_team} has {body}\n{kickoff}\n'

    return message

def build_game_start(start_date, start_time_tbd):
    # Parse the ISO format date string
    dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))

    # Convert to EST
    est = pytz.timezone('US/Eastern')
    dt_est = dt.astimezone(est)

    # Format the date and time
    day = dt_est.strftime('%A')
    date = dt_est.strftime('%m/%d/%Y')

    if not start_time_tbd:
        time = dt_est.strftime('%I:%M%p')
        return f"{day} @ {time} EST ({date})"
    else:
        return f"{day} @ TBD EST ({date})"

def build_stinker_info(fantasy_team, team, week, game, team_record):

    kickoff = build_game_start(game.start_date, game.start_time_tbd)
    message = build_message(fantasy_team, team, week, game, team_record, kickoff)

    home_score = game.home_points if game.completed else 0
    away_score = game.away_points if game.completed else 0

    stinker = create_stinker(team=team, record=team_record)
    game_info = create_game_info(game_id=game.id, game_complete=game.completed, home_team=game.home_team, home_score=home_score, away_team=game.away_team, away_score=away_score, kickoff=kickoff)
    stinker_info = create_stinker_info(fantasy_team=fantasy_team, stinker=stinker, game_info=game_info, text_line=message)

    return stinker_info

def format_date(week_str):
    parts = week_str.split("-")
    extracted_date = parts[1].strip()
    return extracted_date + "/" + CURRENT_YEAR

def extract_week(week_str):
    return int(week_str.split("-")[0].split(" ")[1].strip())

def get_bottom_games(teams, games):
    return {team: games[team] for team in teams if team in games}

async def find_stinkers(target_date, send_message, fantasy_teams):
    week = extract_week(target_date)

    # Parse date from enum string
    target_date = format_date(target_date)

    # Build the next week's games we care about
    next_week_games = get_next_week_games(week)
    next_week_relevant_games_map = filter_games_by_conferences(next_week_games, ACCEPTABLE_CONFERENCES)

    # Get FPI Ratings Map
    fpi_ratings_map = get_fpi_ratings_map(next_week_relevant_games_map)

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
        team_record = records_dict.get(team, '0-0')

        stinker_info = build_stinker_info(fantasy_team, team, week, next_game, team_record)
        stinker_info_list.append(stinker_info)

    # Build the response object
    full_text_body = "\n".join([stinker_info.text_line for stinker_info in stinker_info_list])
    message_info = create_message_info(send_message=send_message, body=full_text_body)
    stinker_week = create_stinker_week(week=week, date=target_date, stinkers=stinker_info_list, message_info=message_info)

    return stinker_week

def build_db_stinker(game, db_stinker: DBStinker, status: DBGameStatus, scoreboard):
    home_score = 0
    away_score = 0

    if status == DBGameStatus.IN_PROGRESS:
        scoreboard_game = get_game_from_scoreboard(game.id, scoreboard)
        if scoreboard_game is not None:
            home_score = scoreboard_game.home_team.points
            away_score = scoreboard_game.away_team.points

    elif status == DBGameStatus.COMPLETE:
        home_score = game.home_points
        away_score = game.away_points

    db_stinker.home_score = home_score
    db_stinker.away_score = away_score
    db_stinker.game_status = status

    return db_stinker

def get_game_from_scoreboard(game_id, scoreboard):
    for game in scoreboard:
        if game.id == game_id:
            return game

    return None
