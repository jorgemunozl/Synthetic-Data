import os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




prompt_mine1= """A flowchart empty"""

"""
"nodes": [
    { "id": "n1", "type": "start", "label": "Inicio" },
    { "id": "n2", "type": "decision", "label": "¿Quieres café?" },
    { "id": "n3", "type": "decision", "label": "¿Hay café?" },
    { "id": "n4", "type": "task", "label": "Hacer café" },
  ],
  "edges": [
    { "id": "e1", "from": "n1", "to": "n2", "condition": null },
    { "id": "e2", "from": "n2", "to": "n10", "condition": "NO" },
    { "id": "e3", "from": "n2", "to": "n3", "condition": "SI" },
    { "id": "e4", "from": "n3", "to": "n5", "condition": "SI" },
    { "id": "e5", "from": "n3", "to": "n4", "condition": "NO" },
  ]
"""


response = client.images.generate(
    model="dall-e-3",
    prompt=prompt_mine1,
    size="1024x1024",
    quality="standard",
    n=1,
)

image_url = response.data[0].url

print("Generated image URL:", image_url)
img_data = requests.get(image_url).content

with open('generated_image.png','wb') as f:
    f.write(img_data)
print("Well")
