from typing import Union
from datetime import date

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from constants import WEEKS, FANTASY_TEAMS

import badTeam

class Teams(BaseModel):
    teams: List[str] = FANTASY_TEAMS

app = FastAPI()

@app.post("/stinkers")
def find_stinkers(fantasyTeams: Teams, week: str = Query(WEEKS[0], enum=WEEKS), sendText: bool = False):
    stinkers = badTeam.main(week, sendText, fantasyTeams.teams)
    return {"stinkers": stinkers}