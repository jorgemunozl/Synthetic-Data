import requests

url = "http://localhost:8000/download-zip"
data = {
    "prompt": [
        "Create a cooking recipe flowchart",
        "Design a meal planning workflow", 
        "Build a kitchen organization process"
    ],  # Now using list of prompts
    "difficulty": 1
}

response = requests.post(url, json=data)

# Check if request was successful
if response.status_code == 200:
    with open("batch_cooking_flowcharts.zip", "wb") as f:
        f.write(response.content)
    print(f"File size: {len(response.content)} bytes")
else:
    print(f"Error: {response.status_code}")
    print(f"Response: {response.text}")