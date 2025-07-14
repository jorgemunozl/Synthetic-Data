import asyncio
import json
from nodes import generateVariants, createImage, generateTopic
from state import State
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


async def main(run_first_time: bool):
    thread_id = "session-1"
    builder = StateGraph(State)
    builder.add_node("generateVariants", generateVariants)
    builder.add_node("validator", validator)
    builder.add_node("tweaker", tweaker)
    builder.add_node("createImage", createImage)
    builder.add_node("generateTopic", generateTopic)
    builder.add_edge(START, "generateTopic")

    if run_first_time:
        initial_dict = {
            "messages": [],
            "seed": "",
            "actual_number": 0,
            "topic": "",
            "number_generations": 0,
            "schemas_generations": [],
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


if __name__ == "__main__":
    asyncio.run(main(True))
