from cfbd_api import get_defensive_weekly_stats

async def get_weekly_tackles(week_number: int):
    # Call service method to get weekly tackles
    api_response = get_defensive_weekly_stats(week_number)

    stats_dict = {}

    for game in api_response:
        for team in game['teams']:
            if team['conference'] == 'Big Ten':
                school = team['school']
                defensive_category = team['categories'][0]  # Get first item from categories

                if defensive_category['name'] == 'defensive':
                    for type_data in defensive_category['types']:
                        if type_data['name'] == 'TOT':
                            for athlete in type_data['athletes']:
                                name = athlete['name']
                                stat = athlete['stat']
                                key = f"{name} ({school})"
                                stats_dict[key] = stat

    return stats_dict

