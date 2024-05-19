from typing import Union
from datetime import date

from fastapi import FastAPI, Query
from constants import WEEKS

import badTeam

app = FastAPI()

@app.get("/stinkers")
def get_stinkers(week: str = Query(WEEKS[0], enum=WEEKS), sendText: bool = False):
    stinkers = badTeam.main(week, sendText)
    return {"stinkers": stinkers}