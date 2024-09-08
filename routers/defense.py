from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import JSONResponse
from models.defense import DefensiveStatsRequest, WeeklyTackleStats, TackleStat
from services.defense import get_weekly_tackles
from services.security import get_api_key
from typing import Dict, Any

router = APIRouter(
    prefix="/defense",
    tags=["Defense"],
    dependencies=[Security(get_api_key)]
)

def format_weekly_tackle_stats(week: int, stats_dict: Dict[str, Any]) -> Dict[str, Any]:
    formatted_stats = []
    for player, tackles in stats_dict.items():
        formatted_stats.append({
            "player": player,
            "tackles": int(tackles)
        })

    return {
        "week": week,
        "stats": formatted_stats
    }

@router.get("/weekly-stats")
async def get_weekly_stats(
    request: DefensiveStatsRequest = Depends()
):
    week_number = int(request.week.name.split('_')[1])
    stats_dict = await get_weekly_tackles(week_number)

    formatted_stats = format_weekly_tackle_stats(week_number, stats_dict)

    return JSONResponse(content=formatted_stats)

