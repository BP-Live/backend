import common.config as config
from openai import OpenAI
from tortoise import fields, models
from fastapi import (
    APIRouter, 
    HTTPException, 
    status, 
    Response,
    Request,
    Depends,
)

import os
import json
import os

openai = OpenAI()

router = APIRouter(tags=["accounts"])

# get the content of prompt.txt
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to prompt.txt
prompt_file = os.path.join(current_dir, "prompt.txt")

with open(prompt_file, "r") as f:
    PROMPT = f.read()
    
def gpt_response(msg: str):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        temperature=0.5,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
        
    # save the to a variable as json
    
    response_json = json.loads(response.choices[0].message.content)
    
    return response_json

@router.post("/")
async def gpt(msg: str):        
    return gpt_response(msg)