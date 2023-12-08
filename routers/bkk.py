import common.config as config
from common.bkk_api import bkk_api
from tortoise import fields, models
from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Response,
    Request,
    Depends,
)

router = APIRouter(tags=["bkk"])

@router.get("/")
async def get_vehicle_positions():        
    return bkk_api.get_vehicle_positions()