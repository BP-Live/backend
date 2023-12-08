from . import config
import os
import json

from openai import OpenAI

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# get the content of prompt.txt
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to prompt.txt
prompt_file = os.path.join(current_dir, "prompt.txt")

with open(prompt_file, "r") as f:
    PROMPT = f.read()
    
def gpt_response(msg: str):
    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
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