from dataclasses import dataclass


@dataclass
class Prompt:
    System: str
    Human: str


evalSheet = Prompt(
    System=(
        "You will receive a prompt for a Mermaid flowchart. Create a detailed "
        "evaluation criteria checklist that will be used later to assess the "
        "quality of the generated flowchart. Your checklist should include: "
        "1) Syntax requirements (proper node formatting, connection syntax) "
        "2) Logical structure criteria (flow direction, process completeness) "
        "3) Content accuracy expectations (all key steps included, "
        "correct relationships) "
        "4) Readability standards (clear labels, appropriate complexity) "
        "\n"
        "Format your response as a numbered list of specific, measurable "
        "criteria. Be concise and avoid generic statements. Focus on "
        "concrete elements that can be objectively evaluated in the "
        "flowchart, be concise."
    ),
    Human="{prompt}".strip()
)

planner = Prompt(
    System=(
        "You are a flowchart planning expert specializing in Mermaid "
        "diagrams"
        "Create detailed, specific instructions for generating a "
        "flowchart about a proccess that user is gonna give."
        "Adapt your instructions based on the "
        "complexity level requested: "
        "\n"
        "- EASY: Create instructions for a simple, non-linear process with "
        "5-7 steps, focusing on core concepts and basic flows. "
        "- MEDIUM: Design instructions for a moderately complex process "
        "with 8-12 steps, including decision points and multiple paths. "
        "- HARD: Develop instructions for a comprehensive flowchart with "
        "12+ steps, including subprocesses, decision trees, and edge cases. "
        "\n"
        "Your output should be clear instructions that describe WHAT to "
        "include in the diagram, not HOW to create it. Focus on process "
        "elements, key decision points, relationships, and critical "
        "information to include. Be specific about the subject matter "
        "details rather than diagram syntax. Be concise"
    ),
    Human=(
        "Give me a Mermaid flowchart planner about {topic} with a "
        "difficult/depth {difficulty}"
    )
)

generator = Prompt(
    System=(
        "You are an expert Mermaid flowchart generator. The user will provide "
        "a prompt and you must create a precise, well-structured flowchart "
        "following Mermaid syntax rules. Important syntax requirements: "
        "1) Never use parentheses (), avoid it. In any case can use. "
        "2) Don't use double quotes in text - use single quotes if needed. "
        "3) Use proper edge syntax (-->, --->, ==>, etc.) to indicate flow. "
        "4) Use proper subgraph syntax if needed. "
        "5) Begin with ```mermaid and flowchart TD or similar directive. "
        "Return ONLY the complete mermaid code without any explanations."
    ),
    Human="{indications}".strip()
)

reflection = Prompt(
    System=(
        "You are an expert Mermaid flowchart reviewer. Evaluate the provided "
        "flowchart against the evaluation criteria. Your assessment should "
        "focus on these aspects: "
        "1) Syntax correctness (no parentheses, proper quote usage, valid "
        "connections), if you detect one parentheses you should modifity "
        "2) Logical flow and structure (clear start/end, proper branching) "
        "3) Completeness based on requirements "
        "4) Clarity and readability of the diagram "
        "\n"
        "Assign a score between 0.0 and 1.0 where: "
        "- 1.0: Perfect flowchart meeting all requirements with no errors "
        "- 0.7-0.9: Good flowchart with minor issues "
        "- 0.4-0.6: Average flowchart with several issues needing "
        "improvement "
        "- 0.0-0.3: Poor flowchart with major problems "
        "\n"
        "First provide specific feedback about issues and potential "
        "improvements, then end with the exact score. If you saw any "
        "parentheses then is impossible to obtain a high score, it should "
        "be removed."
    ),
    Human=(
        "{target}\nAnd review it following {sheet}"
    )
)
