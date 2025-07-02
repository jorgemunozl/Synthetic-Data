import asyncio
import json
from nodes import generate_variants, createImage, route
from state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


async def main(run_first_time: bool):
    thread_id = "session-1"
    initial = ({
            "messages": [],
            "seed": "",
            "number_generations": 0,
            "schemas_generations": []
        }
            if run_first_time
            else {}
        )

    # Build the graph inside the function
    builder = StateGraph(State)
    builder.add_node("generate_variants", generate_variants)
    builder.add_node("createImage", createImage)
    builder.add_edge(START, "generate_variants")
    builder.add_edge("generate_variants", "createImage")
    builder.add_conditional_edges(
        "createImage",
        route,
        {
            "generate_variants": "generate_variants",
            "__end__": END,
        }
    )

    async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as saver:
        graph = builder.compile(checkpointer=saver)
        result = await graph.ainvoke(initial, config={"configurable": {"thread_id": thread_id}})
        snapshot = await graph.aget_state(config={"configurable": {"thread_id": thread_id}})
        latest_state = snapshot.values
        NUM_IMAGE = latest_state["number_generations"]
        print("-> Actual number of generated schemas: ", NUM_IMAGE)
        list_of_dicts = [
            item if isinstance(item, dict) else item.model_dump()
            for item in result["schemas_generations"]
        ]
        name = 'outputModel/schemas_generations.json'
        with open(name, 'w', encoding='utf-8') as f:
            json.dump(list_of_dicts, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main(False))
