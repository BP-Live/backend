import common.config as config
import common.gpt_api as gpt_api
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

router = APIRouter(tags=["gpt"])

@router.post("")
async def gpt(msg: str):    
    return gpt_api.gpt_response(msg)
