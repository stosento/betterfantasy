import os
from dotenv import load_dotenv
from fastapi import FastAPI, Security, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List
from services.webhook import send_message_to_webhook
from services.build_stinkers import find_stinkers
from services.security import get_api_key
from logger import setup_logging
from database import get_db, engine
from services.database_utils import clear_all_tables
import models
from models.stinkers import Week, StinkersRequest, StinkersResultsRequest, StinkerWeek, StinkerInfo, Stinker, GameInfo, MessageInfo
from models.db_models import Week as DBWeek, Stinker as DBStinker
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Validate database connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("Database connection was successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise e  # Re-raise the exception to prevent the app from starting with a bad DB connection
    
    yield
    
    # Shutdown: You can add any cleanup logic here if needed
    print("Shutting down the application")

load_dotenv()
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
logger = setup_logging()

app = FastAPI(title="BetterFantasy API", lifespan=lifespan)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Hello, FastAPI!"}

@app.post("/clear-tables", tags=["Admin"], dependencies=[Security(get_api_key)])
async def clear_tables(db: Session = Depends(get_db)):
    try:
        clear_all_tables(db)
        return {"message": "All tables have been cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while clearing tables: {str(e)}")

@app.post("/stinkers", tags=["Stinkers"], response_model=StinkerWeek, dependencies=[Security(get_api_key)])
async def create_stinkers(
    request: StinkersRequest,
    week: Week,
    overwrite: bool = False,
    send_message: bool = False,
    db: Session = Depends(get_db)
):
    """
    Find and assign stinkers for the specified week.

    This endpoint allows you to:
    - Assign stinkers to fantasy teams for a specific week
    - Optionally overwrite existing stinkers
    - Optionally send a message with the results

    The response includes the assigned stinkers and message information.
    """
    # Extract week number from the Week enum
    week_number = int(week.name.split('_')[1])
    existing_week = db.query(DBWeek).filter(DBWeek.week_number == week_number).first()

    if existing_week and not overwrite:
        stinkers = db.query(DBStinker).filter(DBStinker.week_number == week_number).all()
        stinker_week = StinkerWeek(
            week=existing_week.week_number,
            date=existing_week.date,
            stinkers=[
                StinkerInfo(
                    fantasy_team=stinker.fantasy_team,
                    stinker=Stinker(team=stinker.stinker_team, record=stinker.stinker_record),
                    game_info=GameInfo(
                        game_id=stinker.game_id,
                        game_complete=stinker.game_complete,
                        home_team=stinker.home_team,
                        home_score=stinker.home_score,
                        away_team=stinker.away_team,
                        away_score=stinker.away_score,
                        kickoff=stinker.kickoff
                    ),
                    text_line=stinker.text_line
                ) for stinker in stinkers
            ],
            message_info=MessageInfo(
                send_message=send_message,
                body="\n".join([stinker.text_line for stinker in stinkers])
            )
        )
    else:
        if existing_week:
            # Remove existing stinkers for this week
            db.query(DBStinker).filter(DBStinker.week_number == week_number).delete()
            # Update existing week instead of deleting and reinserting
            existing_week.date = week.value  # Assuming Week.value contains the date string
            db.flush()
        else:
            existing_week = DBWeek(week_number=week_number, date=week.value)
            db.add(existing_week)
            db.flush()

        stinker_week = await find_stinkers(week.value, send_message, request.teams)

        for stinker in stinker_week.stinkers:
            db_stinker = DBStinker(
                week_number=week_number,
                fantasy_team=stinker.fantasy_team,
                stinker_team=stinker.stinker.team,
                stinker_record=stinker.stinker.record,
                game_id=stinker.game_info.game_id,
                game_complete=stinker.game_info.game_complete,
                home_team=stinker.game_info.home_team,
                home_score=stinker.game_info.home_score,
                away_team=stinker.game_info.away_team,
                away_score=stinker.game_info.away_score,
                kickoff=stinker.game_info.kickoff,
                text_line=stinker.text_line
            )
            db.add(db_stinker)

        db.commit()
    if send_message:
        await send_message_to_webhook(WEBHOOK_URL, stinker_week.message_info.body)
    
    return stinker_week

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