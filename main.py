from nodes import plannerNode, generatorNode, reflector
from nodes import evalSheetNode, image, router
from state import State
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse


async def main(prompt: str, diff: str):
    thread_id = "session-1"
    builder = StateGraph(State)
    builder.add_node("planner", plannerNode)
    builder.add_node("generator", generatorNode)
    builder.add_node("reflector", reflector)
    builder.add_node("evalSheet", evalSheetNode)
    builder.add_node("router", router)
    builder.add_node("image", image)
    builder.add_edge(START, "planner")
    builder.add_edge("image", END)

    initial_dict = {
            "messages": [],
            "plannerOutput": "",
            "generatorOutput": "",
            "evalSheet": "",
            "recursion": 0,
            "schemas_generations": [],
            "score": 0.0,
            "filepath": "",
            "promptUser": prompt,
            "diffUser": diff
        }

    initial = State(**initial_dict)
    graph = builder.compile()
    result = await graph.ainvoke(
            initial,
            config=RunnableConfig(
                recursion_limit=10_000,
                configurable={"thread_id": thread_id}
            )
        )
    return result["filepath"]

app = FastAPI()


# Lack parser
@app.get("/images")
async def read_prompt(promptUser: str = Query(..., description="Prompt:"),
                      DiffUser: str = Query(..., description="Difficulty:")
                      ):
    filepath = await main(promptUser, DiffUser)
    return FileResponse(filepath, media_type="image/png")
