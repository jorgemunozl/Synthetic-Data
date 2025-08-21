from fastapi import FastAPI, Query
import asyncio  # Import asyncio
from random import randint
from fastapi.responses import FileResponse


app = FastAPI()


async def main():
    print("Starting process...")
    for i in range(3):
        await asyncio.sleep(1)  # Non-blocking wait
        print(f"Step {i} completed")

    result = randint(1, 100)  # Random integer between 1-100
    print(f"Generated random number: {result}")
    return result


@app.get("/images")
async def read_prompt(promptUser: str = Query(..., description="Prompt:"),
                      DiffUser: str = Query(..., description="Difficulty:")):
    number = await main()
    print(number)
    return FileResponse("images/5da2cd3b-ff16-4211-8a6d-69fc8ac5807b.png", media_type="image/png")


# Add a quick endpoint to test concurrency
@app.get("/quick")
async def quick_response():
    return {"message": "This responds immediately!"}
