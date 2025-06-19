import os
import json
from openai import OpenAI

# -----

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# -----

#file = client.files.create() only works for pdfs and jsonl (finetuning) ! (and more stuff) 

# -----

with open('example.json') as f:
    data = f.read()
# -----
response = client.responses.create(
    model="gpt-4.1", #o3 
    input=[
        {
            "role": "user",
            "content": [
                {
                   "type": "input_text",
                   "text": "give the prompt to generate a turtle",   #"Give me the structure of the follow JSON" + data,
                },
            ]
        }
    ],
    
    #incomplete_details= {},
    instructions      = "Only do exactly what I ask you, nothing else",
    max_output_tokens = 50, #min 16
    temperature       =1.0, #2>t>0
    top_p             =1.0,
)

print(response.output_text)
