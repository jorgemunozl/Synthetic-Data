import asyncio
from nodes import (STT, function_calling, TTS, VLA, router, supervisor)
from state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


async def main(run_first_time: bool):
    thread_id = "session-1"
    builder = StateGraph(State)
    builder.add_node("STT", STT)
    builder.add_node("function_calling", function_calling)
    builder.add_node("TTS", TTS)
    builder.add_node("router", router)
    builder.add_node("supervisor", supervisor)
    #builder.add_node("vision_model", vision_model)
    builder.add_node("VLA", VLA)
    builder.add_edge(START, "STT")
    builder.add_edge("router", END)

    if run_first_time:
        initial_dict = {
            "messages": [],
            "number_step": 0,
            "tts": "",
            "human_prompt": "",
            "step_limit": 2,
        }
    else:
        async with AsyncSqliteSaver.from_conn_string(
            "checkpoint.sqlite"
        ) as saver:
            graph = builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(
                config={"configurable": {"thread_id": thread_id}}
            )
            initial_dict = dict(snapshot.values)

    initial = State(**initial_dict)

    async with AsyncSqliteSaver.from_conn_string(
        "checkpoint.sqlite"
    ) as saver:
        graph = builder.compile(checkpointer=saver)
        result = await graph.ainvoke(
            initial, config={"configurable": {"thread_id": thread_id}}
        )
        snapshot = await graph.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        latest_state = snapshot.values
        print(latest_state)

if __name__ == "__main__":
    asyncio.run(main(True))
