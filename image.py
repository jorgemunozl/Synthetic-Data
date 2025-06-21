import os, requests
from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from openai import OpenAI

# ---- CONFIG ----
#os.environ["OPENAI_API_KEY"] = "sk-…"  # your key here
numImages = 3

# ---- TOOLS ----
def createImage(prompt: str, name: str, size: str="1024x1024", quality: str="standard") -> str:
    client = OpenAI()
    resp = client.images.generate(model="dall-e-3", prompt=prompt, size=size, quality=quality, n=1)
    url = resp.data[0].url
    data = requests.get(url).content
    os.makedirs("images", exist_ok=True)
    path = os.path.join("images", name)
    with open(path, "wb") as f:
        f.write(data)
    return path

# Bind the tool to the LLM
gpt = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools([createImage])

# ---- STATE ----
class State(MessagesState):
    count: int

# ---- NODES ----
# 1) Chat node — asks for a prompt + tool call every time
sys_msg = SystemMessage(content="You create one image per turn.")
def chat_node(state: State) -> dict:
    # Re‑inject system + history + instruction each loop
    instr = HumanMessage(content="Please think of an image, then call createImage(prompt, filename).")
    ctx = [sys_msg] + state["messages"] + [instr]
    resp: AIMessage = gpt.invoke(ctx)
    return {"messages": [resp], "count": state["count"] + 1}

# 2) Loop back or end after tool
def route_after_tool(state: State) -> Literal["chat", "__end__"]:
    return "__end__" if state["count"] >= numImages else "chat"

# ---- BUILD THE GRAPH ----
builder = StateGraph(State)

builder.add_node("chat",     chat_node)
builder.add_node("tools",    ToolNode([createImage]))

# 1. Start in chat
builder.add_edge(START, "chat")

# 2. From chat → either go to tools or end
builder.add_conditional_edges(
    "chat",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

# 3. After tools → either loop back to chat or end
builder.add_conditional_edges(
    "tools",
    route_after_tool,
    {
        "chat": "chat",
        "__end__": END
    }
)

graph = builder.compile()

# ---- RUN IT ----
initial = {
    "messages": [HumanMessage(content="Begin!")],
    "count":    0
}

result = graph.invoke(initial)

print("\nFinal messages:")
for msg in result["messages"]:
    msg.pretty_print()
