from __future__ import annotations
import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel, EmailStr
from monday import board_processing

app = FastAPI()


from typing import Any, Optional

fake_id = 0

def process_data(detail):
    column_title = detail["event"]["columnTitle"]
    boardId = detail["event"]["boardId"]
    pulseId = detail["event"]["pulseId"]
    global fake_id
    if fake_id == 1:
        fake_id = 0
        print('Process runs only onces ------------->')
        return
    else:
        fake_id = 1
        board_processing(boardId, pulseId, column_title)


# @app.post("/text2/", response_model=My_model)
# async def post_board(detail: My_model):
#     return detail
@app.get("/")
async def index():
    return {'data': 'api is working'}

@app.post("/text")
async def create_user(data=Body(...)):
    print(data)
    if "challenge" in data:
        return data
    else:
        process_data(data)
        return {"data" : 'processing is done'}
    # return data


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8020)
