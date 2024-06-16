import os
from typing import Union
from datetime import date
from dotenv import load_dotenv

import httpx
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS

from models.stinkers import StinkerWeek

import badTeam
import logging

load_dotenv()
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the logger
logger = logging.getLogger(__name__)

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI()

async def send_message_to_webhook(message):
    async with httpx.AsyncClient() as client:
        payload = {
            "content": message
        }
        response = await client.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            logger.info("Message sent to webhook successfully")
        else:
            logger.error(f"Failed to send message to webhook. Status code: {response.status_code}")

@app.get("/")
async def read_root():
    logger.info('Read root')
    print('READING ROOT')
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", response_model=StinkerWeek)
async def find_stinkers(fantasy_teams: Teams, 
                  week: str = Query(WEEKS[0], enum=WEEKS), 
                  send_requested: bool = False):
    stinkers = await badTeam.main(week, send_requested, fantasy_teams.teams)
    if send_requested:
        await send_message_to_webhook(stinkers.message_info.body)
    return stinkers