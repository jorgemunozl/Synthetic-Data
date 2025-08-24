from nodes import plannerNode, generatorNode, reflector
from nodes import evalSheetNode, image, router
from state import State
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import io, zipfile
import tempfile
import os


class FlowchartRequest(BaseModel):
    prompt: str
    difficulty: str


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
    return result["imagesGenerated"], result["mermaidGenerated"]

app = FastAPI()


@app.get("/download-zip")
async def create_zip(promptUser: str = Query(..., description="Prompt:"),
                     DiffUser: str = Query(..., description="Difficulty:")
                     ):
    images, mermaid = await main(promptUser, DiffUser)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i in range(len(images)):
            if os.path.exists(images[i]):
                zipf.write(images[i], f"images/{images[i]}")
            else:
                zipf.writestr(f"images/{image}", f"Placeholder for {image}")
            zipf.writestr(f"mermaid/{images[i][:-4]}.mmd", mermaid[i])
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="generated_files.zip",
        headers={"Content-Disposition": "attachment; filename=generated_files.zip"}
    )
