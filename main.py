from typing import Union
from datetime import date

import asyncio
import discord

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS

from models.stinkers import StinkerWeek

import badTeam
import logging

# Configure the logging module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the asyncio logger
logger = logging.getLogger('asyncio')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.reactions = True
client = discord.Client(intents=intents)

print('client', client.application_id)

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI()

async def send_message(message):
    channel = client.get_channel(1250589505375830019)
    await channel.send(message)

@client.event
async def on_ready():
    logger.info('Connecting to channel')
    channel = client.get_channel(1250589505375830019)
    await channel.send('hello')

@client.event
async def on_message(message):
    if message.content.startswith('!hello'):
        await message.channel.send('Hello! I am a Discord bot.')
        channel = client.get_channel(1250589505375830019)
        await channel.send('hello')

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/stinkers", response_model=StinkerWeek)
async def find_stinkers(fantasyTeams: Teams, 
                  week: str = Query(WEEKS[0], enum=WEEKS), 
                  sendText: bool = False):
    stinkers = await badTeam.main(week, sendText, fantasyTeams.teams)
    if (sendText):
        await send_message(stinkers.text_info.body)
    return stinkers

async def start_fastapi():
    import uvicorn
    logger.info('Starting the fastapi server')
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def start_discord_bot():
    logger.info('Starting Discord bot')
    await client.start('MTI1MDU5MTcwMTcxODc5ODQ2Ng.GNlsH9.besqfRArjT4pmsIlXcZ7nLGFm_1rIONCmjNFK0') #token

async def main():
    print('Starting main')
    logger.info('Starting the main coroutine')
    fastapi_task = asyncio.create_task(start_fastapi())
    discord_bot_task = asyncio.create_task(start_discord_bot())

    await asyncio.gather(fastapi_task, discord_bot_task)

if __name__ == "__main__":
    asyncio.run(main())