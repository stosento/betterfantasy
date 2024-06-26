import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List
from constants import WEEKS, FANTASY_TEAMS
from models.stinkers import Week, StinkersRequest, StinkersResultsRequest, StinkerWeek, FANTASY_TEAMS
from logger import setup_logging
from services.webhook import send_message_to_webhook
from services.build_stinkers import find_stinkers, get_stinkers_results
from services.security import get_api_key

from database import database

load_dotenv()
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

logger = setup_logging()

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI(title="BetterFantasy API")

# @app.on_event("startup")
# async def startup():
#     await database["db"].connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database["db"].disconnect()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", tags=["Stinkers"], response_model=StinkerWeek, dependencies=[Security(get_api_key)])
async def create_stinkers( request: StinkersRequest, 
    week: Week, 
    overwrite: bool = False, 
    send_message: bool = False):
    """
    Find and assign stinkers for the specified week.

    This endpoint allows you to:
    - Assign stinkers to fantasy teams for a specific week
    - Optionally overwrite existing stinkers
    - Optionally send a message with the results

    The response includes the assigned stinkers and message information.
    """

    # TODO -- Check to see if exists from DB

    # TODO -- If not exists from DB or overwrite is true, build the stinkers

    stinkers = await find_stinkers(week.value, 
                                   send_message, 
                                   request.teams)
    if send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinkers.message_info.body)
    return stinkers

@app.get("/stinkers", tags=["Stinkers"], dependencies=[Security(get_api_key)])
async def get_stinkers_results(request: StinkersResultsRequest = Depends()):
    """
    Retrieve stinker results for the specified week.

    This endpoint allows you to:
    - Get stinker results for a specific week
    - Optionally send a message with the results

    The response includes the stinker results and, if requested, sends a message to the webhook.
    """
    stinkers_results = get_stinkers_results(request.week)
    if request.send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinkers_results)
    return stinkers_results