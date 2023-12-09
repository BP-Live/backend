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
from common import find_competitors

async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()

        await websocket.send_json({"progress": random.randint(1, 5)})

        data = await websocket.receive_json()
        prompt = data["prompt"]

        response_json = gpt_api.gpt_response(prompt)

        if response_json["location"].lower() == "user":
            lng, lat = data["longitude"], data["latitude"]
        else:
            geocode = bkk_api.geocode_location(response_json["location"])[0]["geometry"]["location"]
            lng, lat = geocode["lng"], geocode["lat"]

        location_name = bkk_api.reverse_geocode(lat, lng)

        await websocket.send_json(
            {
                "metadata": {
                    "type": response_json["business_type"],
                    "name": response_json["business_name"],
                    "location": {"lat": lat, "lng": lng},
                    "location_name": location_name,
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

        competitors = find_competitors.find_competitors(response_json["business_type"], lat, lng)
        await websocket.send_json(competitors)

        await websocket.send_json({"progress": random.randint(50, 60)})

        await asyncio.sleep(1)

        await websocket.send_json({"progress": random.randint(65, 75)})

        await asyncio.sleep(1)

        open_premises = find_competitors.find_open_premises(lat, lng)
        await websocket.send_json({"premises": open_premises})

        await websocket.send_json({"progress": random.randint(80, 85)})

        await asyncio.sleep(1)

        await websocket.send_json({"progress": 100})
    except Exception as e:
        await websocket.send_json({"error": str(e), "trace": traceback.format_exc()})
    await websocket.close()