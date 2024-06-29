from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session

from database import get_db
from services.security import get_api_key
from services.database_utils import clear_all_tables

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Security(get_api_key)]
)

@router.post("/clear-tables")
async def clear_tables(
    db: Session = Depends(get_db)
):
    try:
        clear_all_tables(db)
        return {"message": "All tables have been cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while clearing tables: {str(e)}")