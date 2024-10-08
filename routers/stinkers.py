from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from config import settings
from database import get_db
from models.stinkers import Week, StinkersRequest, StinkersResultsRequest, StinkerWeek, StinkerInfo, Stinker, GameInfo, MessageInfo
from models.db_models import Week as DBWeek, Stinker as DBStinker, GameStatus as DBGameStatus
from services.security import get_api_key
from services.webhook import send_message_to_webhook
from services.build_stinkers import find_stinkers, build_db_stinker
from services.database_utils import update_db_stinker
from populators.db_stinkers import create_db_stinker, create_stinker_week_from_db
from utils.time import build_game_status
from utils.messages import build_stinker_results_message
from cfbd_api import get_game_by_id, get_scoreboard

from fastapi import Security, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from utils.logger import setup_logging
logger = setup_logging()


router = APIRouter(
    prefix="/stinkers",
    tags=["Stinkers"],
    dependencies=[Security(get_api_key)]
)

@router.post("/", response_model=StinkerWeek, summary="Assign Stinkers for the week")
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
    - Optionally overwrite existing stinker assignments
    - Optionally send a message with the stinker assignments

    The response includes the assigned stinkers and message information.
    """
    # Extract week number from the Week enum
    week_number = int(week.name.split('_')[1])
    logger.info(f"Finding stinkers for week {week_number}")
    logger.info(f"db: {db}")
    try:
        db_existing_week = db.query(DBWeek).filter(DBWeek.week_number == week_number).first()
        logger.info(f"Query for existing week returned: {db_existing_week}")
    except SQLAlchemyError as e:
        logger.error(f"Error querying for existing week: {str(e)}")
        logger.error(f"SQLAlchemy error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Database error when querying for existing week")

    if db_existing_week and not overwrite:
        db_stinkers = db.query(DBStinker).filter(DBStinker.week_number == week_number).all()
        stinker_week = create_stinker_week_from_db(db_existing_week, db_stinkers)
    else:
        if db_existing_week:
            db.query(DBStinker).filter(DBStinker.week_number == week_number).delete()
            db_existing_week.date = week.value
            db.flush()
        else:
            db_existing_week = DBWeek(week_number=week_number, date=week.value)
            db.add(db_existing_week)
            db.flush()

        stinker_week = await find_stinkers(week.value, send_message, request.teams)

        for stinker in stinker_week.stinkers:
            db_stinker = create_db_stinker(week_number, stinker)
            db.add(db_stinker)

        db.commit()

    if send_message:
        await send_message_to_webhook(settings.DISCORD_WEBHOOK_URL, stinker_week.message_info.body)

    return stinker_week

@router.get("/")
async def get_stinkers_results(
    request: StinkersResultsRequest = Depends(),
    db: Session = Depends(get_db)
):
    """
    Retrieve stinker results for the specified week.

    This endpoint allows you to:
    - Get stinker results for a specific week
    - Optionally send a message with the results

    The response includes the stinker results and, if requested, sends a message to the webhook.
    """
    week_number = int(request.week.name.split('_')[1])
    db_existing_week = db.query(DBWeek).filter(DBWeek.week_number == week_number).first()
    stinker_week = None

    if db_existing_week:
        db_stinkers = db.query(DBStinker).filter(DBStinker.week_number == week_number).all()
        scoreboard = get_scoreboard()

        for db_stinker in db_stinkers:

            game = get_game_by_id(db_stinker.game_id)
            game_status = build_game_status(game)
            db_stinker = build_db_stinker(game, db_stinker, game_status, scoreboard)
            update_db_stinker(db_stinker, db)

        stinker_week = create_stinker_week_from_db(db_existing_week, db_stinkers)

    else:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Could not find the stinkers for the specified week."
        )

    message_body = build_stinker_results_message(stinker_week)
    stinker_week.message_info = MessageInfo(send_message=request.send_message, body=message_body)

    # Handle sending message if requested
    if request.send_message:
        await send_message_to_webhook(settings.DISCORD_WEBHOOK_URL, message_body)

    return stinker_week
