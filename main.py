from __future__ import annotations
import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr
import string
from typing import List, Set, Union
import json
from monday import main

app = FastAPI()


from typing import Any, Optional


def process_data(detail):
    column_title = detail["event"]["columnTitle"]
    boardId = detail["event"]["boardId"]
    pulseId = detail["event"]["pulseId"]

    main(boardId, pulseId, column_title)


# @app.post("/text2/", response_model=My_model)
# async def post_board(detail: My_model):
#     return detail
@app.post("/")
async def index():
    return {'data': 'api is working'}

@app.post("/text/")
async def create_user(data=Body(...)):
    print(data)
    if "challenge" in data:
        return data
    else:
        process_data(data)
    # return data


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
