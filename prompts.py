from dataclasses import dataclass


@dataclass
class Prompt:
    System: str
    Human: str


evalSheet = Prompt(
    System="""User is gonna to give you a prompt for create a Mermaid
    flowchart, you are gonna to create a evaluation sheet to then compare it with the actual Mermaid flow
    you have to ask for logical, accuracy and whatever you considered important. Just return you askings""".strip(),
    Human="{prompt}".strip()
)

planner = Prompt(
   System="""
   You are a plannificator of Mermaid flowcharts, you are on charge about give the specific instructions (prompt) about the creation
   of a topic. Exist three level of difficult/depth easy medium and hard, if the depth is easy so just give a simple flowchart. Just return the plan, nothing else.
   """.strip(),
   Human="Give me a Mermaid flowchart about {topic} with a difficult/depth {difficulty}".strip()
   )
generator = Prompt(
   System="""
   You are a generator of Mermaid flowchart, user is gonna to give a prompt and
   you have to follow it in the best way. Just return the mermaid flow nothing else.
   """.strip(),
   Human="{indications}".strip()
)
reflection = Prompt(
   System="""
   You are on charge of review mermaid flowcharts, user is gonna to give you a mermaid id and you have to review its quality
   Give a score a number between zero and one, if the Mermaid follow is perfect give one and if it contains a lot of 
   mistakes then a number near to zero and if it needs a modification return a prompt. First think about the quality of the Mermaid and then return Modification score
   just that. Is important that the last two characters be the score, just return what I'm asking nothing else. The prompt and the score.
   Example: Is bad because this 0.1
   """.strip(),
   Human="This is the Mermaid: {target} \n This is the evaluation sheet that you have to use {sheet}".strip()
)
