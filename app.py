from fastapi import FastAPI, Depends
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi import WebSocket
from tortoise.contrib.fastapi import register_tortoise

import os

import common.config as config
from routers import router
from routers.ws import websocket_endpoint

app = FastAPI(
    default_response_class=ORJSONResponse,
    root_path=config.ROOT_PATH,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/v1")

db_config: dict = {
    'connections': {
        # Dict format for connection
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.environ["DB_HOST"],
                'port': os.environ["DB_PORT"],
                'user': os.environ["DB_USER"],
                'password': os.environ["DB_PASSWORD"],
                'database': os.environ["DB_DATABASE"],
            },
        },
    },
    'apps': {
        'models': {
            'models': ["aerich.models", "routers"],
            # If no default_connection specified, defaults to 'default'
            'default_connection': 'default',
        }
    }
}

register_tortoise(
    app=app,
    config=db_config,
    generate_schemas=False
)

from routers.accounts import Token, require_token
from typing import Annotated

@app.websocket("/ws")
async def ws_endpoint(
    websocket: WebSocket,
    token: Annotated[Token, Depends(require_token)],
):
    response = await websocket_endpoint(websocket)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
