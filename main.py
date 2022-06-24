from __future__ import annotations
from google_sheet_kixie import find_client
from monday import board_processing
from fastapi import FastAPI, Body
import uvicorn
from typing import Any, Optional


app = FastAPI()


fake_id = 0


def process_data(detail):
    column_title = detail["event"]["columnTitle"]
    boardId = detail["event"]["boardId"]
    pulseId = detail["event"]["pulseId"]
    global fake_id
    if fake_id == 1:
        fake_id = 0
        print("Process runs only onces ------------->")
        return
    else:
        fake_id = 1
        board_processing(boardId, pulseId, column_title)


@app.get("/")
async def index():
    return {"data": "api is working"}


@app.post("/text", tags=["Monday.com"])
async def create_user(data=Body(...)):
    print(data)
    if "challenge" in data:
        return data
    else:
        process_data(data)
        return {"data": "processing is done"}
    # return data


# ep used for the kixei power dilar and CRM (google sheet)
@app.get("/api", tags=["Kixie"])
async def call_webhook(number):
    print("\n\n\n\n phone number---------------->", number)
    record = find_client(number)
    if record:
        data = {"found": True}
        data.update(record)
        print("contact data----------->", data)
    else:
        print("no data found")
        data = {"found": False}
        print("contact data----------->", data)

    return data


# ep used for the kixei power dilar and CRM (google sheet)
@app.post("/api", tags=["Kixie"])
async def call_webhook(data=Body(...)):
    print("data is comming from post----------->", data)
    return data


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True)
