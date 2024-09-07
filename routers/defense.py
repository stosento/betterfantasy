from fastapi import APIRouter, Depends, HTTPException, Security
from models.defense import DefensiveStatsRequest, WeeklyTackleStats, TackleStat
from services.defense import get_weekly_tackles
from services.security import get_api_key

router = APIRouter(
    prefix="/defense",
    tags=["Defense"],
    dependencies=[Security(get_api_key)]
)

@router.get("/weekly-stats")
async def get_weekly_stats(
    request: DefensiveStatsRequest = Depends()
):
    week_number = int(request.week.name.split('_')[1])
    stats_dict = get_weekly_tackles(week_number)

    tackle_stats = []
    for player, tackles in stats_dict.items():
        tackle_stats.append(TackleStat(player=player, tackles=int(float(tackles))))

    response = WeeklyTackleStats(week=week_number, stats=tackle_stats)

    # Format response and return
    return response.json()

