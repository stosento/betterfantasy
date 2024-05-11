from typing import Union
from datetime import date

from fastapi import FastAPI

import badTeam

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/stinkers")
def get_stinkers(target_date: date):
    stinkers = badTeam.main(target_date)
    return {"stinkers": stinkers}