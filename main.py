import os
from typing import Union
from datetime import date
from dotenv import load_dotenv

import asyncio
import discord

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS

from models.stinkers import StinkerWeek

import badTeam
import logging

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the asyncio logger
logger = logging.getLogger('asyncio')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
client = discord.Client(intents=intents)

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI()

async def send_message(message):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    await channel.send(message)

@client.event
async def on_ready():
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    logger.info('Discord bot getting channel: ' + str(channel))
    # await channel.send('Wassup bitches?')

@client.event
async def on_message(message):
    logger.info('Message received: ' + message.content)
    if message.content.startswith('!hellobot'): # Not working
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        await channel.send('Heya fartknocker')

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", response_model=StinkerWeek)
async def find_stinkers(fantasy_teams: Teams, 
                  week: str = Query(WEEKS[0], enum=WEEKS), 
                  send_requested: bool = False):
    stinkers = await badTeam.main(week, send_requested, fantasy_teams.teams)
    if (send_requested):
        await send_message(stinkers.message_info.body)
    return stinkers

async def start_fastapi():
    import uvicorn
    logger.info('Starting the fastapi server')
    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_discord_bot():
    logger.info('Starting Discord bot')
    await client.start(DISCORD_BOT_TOKEN)

async def main():
    fastapi_task = asyncio.create_task(start_fastapi())
    discord_bot_task = asyncio.create_task(start_discord_bot())
    await asyncio.gather(fastapi_task, discord_bot_task)

if __name__ == "__main__":
    asyncio.run(main())