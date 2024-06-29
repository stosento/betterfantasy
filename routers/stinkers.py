from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.stinkers import Week, StinkersRequest, StinkersResultsRequest, StinkerWeek, StinkerInfo, Stinker, GameInfo, MessageInfo
from models.db_models import Week as DBWeek, Stinker as DBStinker
from services.security import get_api_key
from services.webhook import send_message_to_webhook
from services.build_stinkers import find_stinkers
from populators.db_stinkers import create_db_stinker, create_stinker_week_from_db

router = APIRouter(
    prefix="/stinkers",
    tags=["Stinkers"],
    dependencies=[Security(get_api_key)]
)

@router.post("/", response_model=StinkerWeek)
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
    db_existing_week = db.query(DBWeek).filter(DBWeek.week_number == week_number).first()

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
    existing_week = db.query(DBWeek).filter(DBWeek.week_number == week_number).first()
    
    if existing_week:
        # Retrieve results from the database
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
            message_info=None  # We'll set this later if send_message is True
        )
    else:
        # Generate new results using the existing function
        stinker_week = await get_stinkers_results(request.week)
        
        # Save the new results to the database
        new_week = DBWeek(week_number=stinker_week.week, date=stinker_week.date)
        db.add(new_week)
        
        for stinker in stinker_week.stinkers:
            db_stinker = create_db_stinker(stinker_week.week, stinker)
            db.add(db_stinker)
        
        db.commit()

    # Handle sending message if requested
    if request.send_message:
        message_body = "\n".join([stinker.text_line for stinker in stinker_week.stinkers])
        await send_message_to_webhook(settings.DISCORD_WEBHOOK_URL, message_body)
        stinker_week.message_info = MessageInfo(send_message=True, body=message_body)

    return stinker_week