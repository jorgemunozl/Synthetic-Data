from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
from prompts import promptTopicHum, promptTopicSys, prompValidator
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid
import re

def parse_score_and_text(response: str):
    pattern = r'^\s*(0(?:\.\d+)?|1(?:\.0+)?)\s+(.*)$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    score = float(m.group(1))
    text = m.group(2).strip()
    return score, text

async def generateTopic(state: State) -> Command[Literal["generateVariants"]]:
    llmTopic = ChatOpenAI(model=GraphConfig().base,
                          temperature=GraphConfig().model_temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptTopicHum),
        ("human", promptTopicSys)
    ])
    chain = prompt | llmTopic
    response = await chain.ainvoke({})
    return Command(update={"topic": response.content}, goto="generateVariants")


async def generateVariants(state: State) -> Command[Literal["createImage"]]:
    llm = ChatOpenAI(model=GraphConfig().base,
                     temperature=GraphConfig().model_temperature)
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    response = await chain.ainvoke(
        {"seed_value": state.seed, "topic": state.topic}
    )
    print(f""" -> Creating the schema number {state.number_generations} a
    with topic : {state.topic}""")
    response = GeneratorVariantOutput.model_validate(response)
    output_model: GeneratorVariantOutput = response
    my_dict = output_model.model_dump()
    my_id = str(uuid.uuid4())
    my_dict["id"] = my_id
    updated = list(state.schemas_generations)
    updated.append(my_dict)
    print(f" -> Schema number {state.number_generations} created!")
    return Command(update={"schemas_generations": updated}, goto="createImage")


def createImage(state: State) -> Command[Literal["generateTopic", "__end__"]]:
    variant = state.schemas_generations[state.number_generations]
    prompt = promptImage(variant)
    print(f" -> Creating the image number {state.number_generations}")
    client = OpenAI()
    response = client.images.generate(
        model=GraphConfig().image,
        prompt=prompt,
        )
    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    dir_path = directoryOutput
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{state.number_generations}.png")
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    print(f" -> Image number {state.number_generations} created")
    stoptIteration = state.actual_number + NUM_IMAGES_TO_ADD
    if (state.number_generations + 1 >= stoptIteration):
        goto = "__end__"
    else:
        goto = "generateTopic"
    return Command(update={"number_generations": state.number_generations+1},
                   goto=goto)


def create_file(path):
    """
    Uploads a file to OpenAI and returns the file_id.
    """
    client = OpenAI()
    with open(path, "rb") as f:
        response = client.files.create(file=f, purpose="vision")
    return response.id


def tweaker(state: State):
    client = OpenAI()

    fileId = create_file(state.pathToImage)
    maskId = create_file("mask.png")

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": state.modification,
                    },
                    {
                        "type": "input_image",
                        "file_id": fileId,
                    }
                ],
            },
        ],
        tools=[
            {
                "type": "image_generation",
                "quality": "high",
                "input_image_mask": {
                    "file_id": maskId,
                },
            },
        ],
    )

    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]

    if image_data:
        image_base64 = image_data[0]
        with open("modification.png", "wb") as f:
            f.write(base64.b64decode(image_base64))

def validator(state: State) -> Command[Literal["tweaker", "generateTopic"]]:
    with open(state.pathToImage, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    uri = f"data:image/png;base64,{b64}"
    variant = state.schemas_generations[state.number_generations]
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4-vision-preview",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompValidator(variant)},
                    {
                        "type": "input_image",
                        "image_url": {"url": uri},
                    },
                ],
            },
        ],
    )
    reply = response.choices[0].message.content
    score, prompt = parse_score_and_text(reply)
    if score >= state.threshold:
        goto = "generateTopic"
    else:
        goto = "tweaker"
    return Command(update={"modification": prompt}, goto=goto)
