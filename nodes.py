from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from state import State
from prompts import promptSystem, promptHuman
#from prompts import promptTopicHum, promptTopicSys, promptValidator
from openai import OpenAI
from constants import directoryOutput
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid
from prompts import planner

print(planner.System)


async def planner(state: State) -> Command[Literal["generator"]]:
    llmTopic = ChatOpenAI(model=GraphConfig().modelBase,
                          temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptTopicSys),
        ("human", promptTopicHum)
    ])
    chain = prompt | llmTopic
    response = await chain.ainvoke({})
    return Command(update={"topic": response.content}, goto="generator")


async def generator(state: State) -> Command[Literal["reflector"]]:
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    print(f""" -> Creating the schema number {state.number_generations}
          with topic : {state.topic}""")
    response = await chain.ainvoke(
        {"seed_value": state.seed, "topic": state.topic}
    )
    response = {"flowchart": response}
    my_id = str(uuid.uuid4())
    response["id"] = my_id
    updated = list(state.schemas_generations)
    updated.append(response)
    print(f" -> Schema number {state.number_generations} created!")
    return Command(update={"schemas_generations": updated}, goto="reflector")


def reflector(state: State) -> Command[Literal["generator", "planner"]]:
    variant = state.schemas_generations[-1]
    
    if (score>=THRESHOLD):
        if condition:
            difficulty+=1
        goto = "planner"
        goto = "imageGenerator"
    else:
        goto = "generator"
    return Command(update={"number_generations": state.number_generations+1,
                          "pathToImage":file_path,"actualRecursion":0},
                   goto=goto)


def validator(state: State) -> Command[Literal["tweaker", "generateTopic","__end__"]]:
    with open(state.pathToImage, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    uri = f"data:image/png;base64,{b64}"
    variant = state.schemas_generations[state.number_generations-1]
    client = OpenAI()
    print(f" -> Watching flowchart about --{state.topic}--")
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": promptValidator(variant,state.threshold)},
                    {
                        "type": "input_image",
                        "image_url": uri,
                    },
                ],
            },
        ],
    )
    reply = response.output_text
    score, prompt = parse_score_and_text(reply)
    print(f"SCORE -> {score}")
    print(f"FEEDBACK -> {prompt}")
    stoptIteration = state.actual_number + NUM_IMAGES_TO_ADD
    if (score >= state.threshold and state.number_generations < stoptIteration):
        goto = "generateTopic"  
    if (score <= state.threshold and state.actualRecursion != state.recursionLimit):
        goto = "tweaker"
    else:
        goto = "__end__"
    print(" -> Modified Numbers : ", state.actualRecursion)
    print(f" -> Going to  : {goto}")
    return Command(update={"modification": prompt}, goto=goto)


def tweaker(state: State) -> Command[Literal["validator"]]:
    client = OpenAI()
    print(" -> Creating modified image ")
    result = client.images.edit(
    quality="high",
    model="gpt-image-1",
    image=[
        open(state.pathToImage, "rb")
    ],
    prompt=state.modification
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(state.pathToImage, "wb") as f:
        f.write(image_bytes)
    print(" -> Image modified created returning to validator")
    return Command(update={"actualRecursion":state.actualRecursion+2},goto="validator")
