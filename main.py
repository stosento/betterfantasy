import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Security, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS
from models.stinkers import StinkerWeek
import build_stinkers
from logger import setup_logging
from webhook import send_message_to_webhook

from database import database

load_dotenv()
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
BF_API_KEYS = os.getenv('BF_API_KEYS').split(',')

logger = setup_logging()

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI(title="BetterFantasy API")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header not in BF_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key_header

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", tags=["Stinkers"], response_model=StinkerWeek, dependencies=[Security(get_api_key)])
async def find_stinkers(fantasy_teams: Teams, 
                        week: str = Query(WEEKS[0], enum=WEEKS), 
                        send_message: bool = False):
    stinkers = await build_stinkers.find_stinkers(week, send_message, fantasy_teams.teams)
    if send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinkers.message_info.body)
    return stinkers

@app.get("/stinkers/results", tags=["Stinkers"], dependencies=[Security(get_api_key)])
async def get_stinkers_results(week: str = Query(WEEKS[0], enum=WEEKS),
                               send_message: bool = False):
    stinkers_results = build_stinkers.get_stinkers_results(week)
    if send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinkers_results)
    return stinkers_results