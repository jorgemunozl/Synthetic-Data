import asyncio
import json
from nodes import plannerNode, generatorNode, reflector, eval_sheet, images, router
from state import State
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


async def main(run_first_time: bool):
    thread_id = "session-1"
    builder = StateGraph(State)
    builder.add_node("planner", plannerNode)
    builder.add_node("evaluation-sheet", evaluation_sheet)
    builder.add_node("generator", generatorNode)
    builder.add_node("reflector", reflector)
    builder.add_node("router", router)
    builder.add_node("images", images)
    builder.add_edge(START, "planner")

    if run_first_time:
        initial_dict = {
            "messages": [],
            "seed": "",
            "actual_number": 0,
            "topic": "",
            "number_generations": 0,
            "schemas_generations": [],
            "pathToImage": "",
            "score": 0,
            "threshold": 0.7,
            "modification": "",
            "recursionLimit": 2,
            "actualRecursion": 0
        }
    else:
        async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as saver:
            graph = builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(
                config={"configurable": {"thread_id": thread_id}}
            )
            initial_dict = dict(snapshot.values)

    initial = State(**initial_dict)

    async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as saver:
        graph = builder.compile(checkpointer=saver)
        result = await graph.ainvoke(
            initial, config={"configurable": {"thread_id": thread_id}}
        )
        snapshot = await graph.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        latest_state = snapshot.values
        num_image = latest_state["number_generations"]  
        print("-> Actual number of generated schemas:", num_image)
        name = "outputModel/schemas_generations.json"
        with open(name, "w") as f:
            json.dump(result["schemas_generations"], f, indent=2)
        print(" -> Schemas saved!")

if __name__ == "__main__":
    asyncio.run(main(False))
