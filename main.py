from typing import Union
from datetime import date

from fastapi import FastAPI, Query
from constants import WEEKS

import badTeam

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/stinkers")
def get_stinkers(week: str = Query(WEEKS[0], enum=WEEKS), sendText: bool = False):
    stinkers = badTeam.main(week, sendText)
    return {"stinkers": stinkers}