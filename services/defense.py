from cfbd_api import get_defensive_weekly_stats
from typing import List, Dict

async def get_weekly_tackles(week_number: int) -> Dict[str, int]:
    # Call service method to get weekly tackles
    api_response = get_defensive_weekly_stats(week_number)

    stats_dict = {}

    for game in api_response:
        # print('game: ', game)
        for team in game.teams:
            # print('team: ', team)
            if team.conference == 'Big Ten':
                school = team.school
                defensive_category = next((cat for cat in team.categories if cat.name == 'defensive'), None)

                if defensive_category:
                    tot_type = next((t for t in defensive_category.types if t.name == 'TOT'), None)

                    if tot_type:
                        for athlete in tot_type.athletes:
                            name = athlete.name
                            stat = int(float(athlete.stat))  # Convert stat to integer, handling potential floats
                            key = f"{name} ({school})"
                            stats_dict[key] = stat

    return stats_dict

