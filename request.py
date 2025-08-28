import requests

url = "http://localhost:8000/download-zip"
data = {
    "prompt": [
        "Create a cooking recipe flowchart",
        "Design a meal planning workflow", 
        "Build a kitchen organization process"
    ], 
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

"""curl -X POST "http://localhost:8000/download-zip"      -H "Content-Type: application/json"      -d '{
       "prompt": [
        "Create a cooking recipe flowchart",
        "Design a meal planning workflow", 
        "Build a kitchen organization process"
       ],
       "difficulty": 1
     }'      -o flowchart.zip
"""
