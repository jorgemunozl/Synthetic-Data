from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
from prompts import promptTopicHum, promptTopicSys, promptValidator
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid
import re


def create_file(path):
    client = OpenAI()
    with open(path, "rb") as f:
        response = client.files.create(file=f, purpose="vision")
    return response.id


def parse_score_and_text(response: str):
    pattern = r'^\s*(0(?:\.\d+)?|1(?:\.0+)?)\s+(.*)$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    score = float(m.group(1))
    text = m.group(2).strip()
    return score, text


async def generateTopic(state: State) -> Command[Literal["generateVariants"]]:
    llmTopic = ChatOpenAI(
        model=GraphConfig().base,
        temperature=GraphConfig().model_temperature
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptTopicHum),
        ("human", promptTopicSys)
    ])
    chain = prompt | llmTopic
    response = await chain.ainvoke({})
    return Command(
        update={"topic": response.content},
        goto="generateVariants"
    )


async def generateVariants(state: State) -> Command[Literal["createImage"]]:
    llm = ChatOpenAI(
        model=GraphConfig().base,
        temperature=GraphConfig().model_temperature
    )
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    response = await chain.ainvoke(
        {"seed_value": state.seed, "topic": state.topic}
    )
    print(f""" -> Creating the schema number {state.number_generations}
    with topic : {state.topic}""")
    response = GeneratorVariantOutput.model_validate(response)
    output_model: GeneratorVariantOutput = response
    my_dict = output_model.model_dump()
    my_id = str(uuid.uuid4())
    my_dict["id"] = my_id
    updated = list(state.schemas_generations)
    updated.append(my_dict)
    print(f" -> Schema number {state.number_generations} created!")
    return Command(
        update={"schemas_generations": updated},
        goto="createImage"
    )


def createImage(state: State) -> Command[Literal["generateTopic",
                                                 "validator"]]:
    variant = state.schemas_generations[state.number_generations]
    id = variant["id"]
    print(f""" -> Creating the image number
          --{state.number_generations}-- about --{state.topic}--""")
    prompt = promptImage(variant)
    client = OpenAI()
    response = client.images.generate(
        model=GraphConfig().image,
        prompt=prompt,
        response_format="b64_json"
    )
    if not response.data:
        print("No image; Response:", response)
        return Command(goto="generateTopic")
    else:
        image_base64 = response.data[0].b64_json
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
            dir_path = directoryOutput
            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, f"{id}.png")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            with open("original.png", "wb") as f:
                f.write(image_bytes)
            print(f" -> Image with: {id} created")
            return Command(
                update={"number_generations": state.number_generations+1,
                        "pathToImage": file_path, "actualRecursion": 0},
                goto="validator"
            )
        else:
            print("No base64 data in response")
            return Command(goto="generateTopic")


def validator(state: State) -> Command[Literal["tweaker",
                                               "generateTopic", "__end__"]]:
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
                    {
                        "type": "input_text",
                        "text": promptValidator(variant, state.threshold)
                    },
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
    if (score >= state.threshold and
            state.number_generations < stoptIteration):
        goto = "generateTopic"
    if (score <= state.threshold and
            state.actualRecursion != state.recursionLimit):
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
    return Command(
        update={"actualRecursion": state.actualRecursion+1},
        goto="validator"
    )
