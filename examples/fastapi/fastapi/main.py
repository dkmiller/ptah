from pathlib import Path
from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World (8)"}


@app.get("/read_text")
def read_text(relative: str):
    path = Path(__file__).parent / relative
    return {"text": path.read_text()}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
