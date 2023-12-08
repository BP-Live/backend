import traceback
import asyncio
import random
from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Response,
    Request,
    Depends,
    WebSocket
)

from common.bkk_api import bkk_api
from common import gpt_api
from routers.accounts import Token, require_token

from typing import Annotated

async def websocket_endpoint(
    websocket: WebSocket,
    token: Annotated[Token, Depends(require_token)],
):
    try:
        await websocket.accept()

        await websocket.send_json({"progress": 0})

        data = await websocket.receive_json()
        prompt = data["prompt"]

        response_json = gpt_api.gpt_response(prompt)

        if response_json["location"].lower() == "user":
            lng, lat = data["longitude"], data["latitude"]
        else:
            geocode = bkk_api.geocode_location(response_json["location"])[0]["geometry"]["location"]
            lng, lat = geocode["lng"], geocode["lat"]

        await websocket.send_json(
            {
                "metadata": {
                    "type": response_json["business_type"],
                    "name": response_json["business_name"],
                    "location": {"lat": lat, "lng": lng},
                }
            }
        )

        await websocket.send_json({"progress": random.randint(5, 15)})

        await asyncio.sleep(1)

        await websocket.send_json(
            {
                "pros": [
                    response_json["pros"]["pro1"],
                    response_json["pros"]["pro2"],
                    response_json["pros"]["pro3"],
                ]
            }
        )

        await websocket.send_json({"progress": random.randint(20, 30)})

        await asyncio.sleep(1)

        await websocket.send_json(
            {
                "cons": [
                    response_json["cons"]["con1"],
                    response_json["cons"]["con2"],
                    response_json["cons"]["con3"],
                ]
            }
        )

        await websocket.send_json({"progress": random.randint(35, 45)})

        await asyncio.sleep(1)

        await websocket.send_json(
            {
                "competitors": [
                    {"lat": 37.7749, "lng": -122.42},
                    {"lat": 37.7769, "lng": -122.4194},
                    {"lat": 37.7759, "lng": -122.4184},
                ]
            }
        )

        await websocket.send_json({"progress": random.randint(50, 60)})

        await asyncio.sleep(1)

        await websocket.send_json({"progress": random.randint(65, 75)})

        await asyncio.sleep(1)

        await websocket.send_json({"progress": random.randint(80, 85)})

        await asyncio.sleep(1)

        await websocket.send_json({"progress": 100})
    except Exception as e:
        await websocket.send_json({"error": str(e), "trace": traceback.format_exc()})
    await websocket.close()