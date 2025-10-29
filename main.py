from nodes import plannerNode, generatorNode, reflector
from nodes import evalSheetNode, image, router
from state import State
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import zipfile
import tempfile
import os


class FlowchartRequest(BaseModel):
    prompt: list[str] = Field(
        default_factory=list,
        description="list of processes"
    )
    difficulty: int = Field(
        gt=0,
        description="Difficulty must be greater than 0"
    )


async def main(prompt: list, diff: int):
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
            "difficultyIndex": 0,
            "actual_number": 0,
            "schemas_generations": [],
            "score": 0.0,
            "promptUser": prompt,
            "diffUser": diff,
            "imagesGenerated": [],
            "mermaidGenerated": [],
            "topicIndex": 0,
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


@app.post("/download-zip")
async def create_zip(request: FlowchartRequest):
    images, mermaid = await main(request.prompt, request.difficulty)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        zip_path = tmp_file.name

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i in range(len(images)):
            if os.path.exists(images[i]):
                filename = os.path.basename(images[i])
                zipf.write(images[i], f"images/{filename}")
            else:
                filename = os.path.basename(images[i])
                zipf.writestr(f"images/{filename}",
                              f"Placeholder for {images[i]}")
            if i < len(mermaid):
                mermaid_filename = os.path.basename(images[i])[:-4] + ".mmd"
                zipf.writestr(f"mermaid/{mermaid_filename}", mermaid[i])

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="generated_files.zip",
        headers={
            "Content-Disposition": "attachment; filename=generated_files.zip"
        }
    )


@app.get("/healthcheck")
async def healthcheck():
    try:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "ok", "details": "GenerateFLowCharts v1"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "detail": str(e)}
        )
