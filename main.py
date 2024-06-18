import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS
from models.stinkers import StinkerWeek
import build_stinkers
from logger import setup_logging
from webhook import send_message_to_webhook

load_dotenv()
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

logger = setup_logging()

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI(title="BetterFantasy API")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", tags=["Stinkers"], response_model=StinkerWeek)
async def find_stinkers(fantasy_teams: Teams, 
                        week: str = Query(WEEKS[0], enum=WEEKS), 
                        send_message: bool = False):
    stinkers = await build_stinkers.find_stinkers(week, send_message, fantasy_teams.teams)
    if send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinkers.message_info.body)
    return stinkers