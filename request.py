import requests

url = "http://localhost:8000/download-zip"
data = {
    "prompt": "Create a cooking recipe flowchart",
    "difficulty": 1
}

response = requests.post(url, json=data)
with open("cooking_flowchart.zip", "wb") as f:
    f.write(response.content)