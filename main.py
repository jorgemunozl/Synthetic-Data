import asyncio
from graph import graph
from constants import NUM_IMAGE_WE_HAVE
import json

async def main():
    initial = {
    "messages": [],
    "seed": "",
    "number_generations": NUM_IMAGE_WE_HAVE + 1,
    "schemas_generations": []
    }
    result = await graph.ainvoke(initial)
    
    with open("numImage.json", "r") as f:
        dataNum = json.load(f)
    dataNum["numImages"] = result["number_generations"] - 1
    with open("numImage.json", "w") as f:
        json.dump(dataNum, f)
    with open('outputModel/schemas_generations.json', 'w', encoding='utf-8') as f:
        json.dump(result["schemas_generations"], f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
