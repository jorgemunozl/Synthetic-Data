import asyncio
from constants import NUM_IMAGE_WE_HAVE
import json
from langgraph.graph import StateGraph, START, END
from nodes import generate_variants, createImage, route
from state import State
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

builder = StateGraph(State)
builder.add_node("generate_variants", generate_variants)
builder.add_node("createImage", createImage)

builder.add_edge(START, "generate_variants")
#builder.add_edge("generate_variants",END)

builder.add_edge("generate_variants", "createImage")
builder.add_conditional_edges(
        "createImage",
            route,
            {
                "generate_variants": "generate_variants",
                "__end__": END,
            },
        )
async def main(run_first_time: bool):
    async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as saver:
        graph = builder.compile(checkpointer=saver)
        initial = ({
        "messages": [],
        "seed": "",
        "number_generations": NUM_IMAGE_WE_HAVE, # We have to use checkpointer and memory!
        "schemas_generations": []
        }
        if run_first_time
        else {}
        )
        
        result = await graph.ainvoke(initial, config={"configurable": {"thread_id": "session-1"}})
        
    with open("numImage.json", "r") as f:
        dataNum = json.load(f)
    dataNum["numImages"] = result["number_generations"]
    with open("numImage.json", "w") as f:
        json.dump(dataNum, f)

    
    list_of_dicts = [
    item if isinstance(item, dict) else item.model_dump()
    for item in result["schemas_generations"]
    ]
    with open('outputModel/schemas_generations.json', 'w', encoding='utf-8') as f:
       json.dump(list_of_dicts, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main(False))
