import os
from dotenv import load_dotenv
from fastapi import FastAPI, Security, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List
from config import settings
from services.webhook import send_message_to_webhook
from services.build_stinkers import find_stinkers
from services.security import get_api_key
from utils.logger import setup_logging
from database import get_db, engine
from routers import stinkers, admin, defense
from services.database_utils import clear_all_tables
import models
from models.stinkers import Week, StinkersRequest, StinkersResultsRequest, StinkerWeek, StinkerInfo, Stinker, GameInfo, MessageInfo
from models.db_models import Week as DBWeek, Stinker as DBStinker
from populators.db_stinkers import create_db_stinker, create_stinker_week_from_db
from sqlalchemy import text

import sys
print(sys.path)
import psycopg2
print(psycopg2.__file__)

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

def create_app() -> FastAPI:
    logger = setup_logging()

    app = FastAPI(title="BetterFantasy API", lifespan=lifespan)

    # Include routers
    app.include_router(stinkers.router)
    app.include_router(defense.router)
    app.include_router(admin.router)

    @app.get("/", tags=["Root"])
    async def read_root():
        return {"message": "Hello, FastAPI!"}

    return app

app = create_app()
