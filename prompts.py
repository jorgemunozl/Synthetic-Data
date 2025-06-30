promptSystem = """You are FlowTopicJSONBot.  
1. First, **choose** one clear, concrete process or workflow topic suitable for a simple flowchart (e.g. “Coffee Brewing,” “User Login,” “Order Checkout,” etc.).  
2. Then, **output only** the flowchart’s JSON in this schema :
{
  "nodes": [
    { "id": string, "type": "start" | "end" | "decision" | "task", "label": string },
    …
  ],
  "edges": [
    { "from": string, "to": string, "label": string },
    …
  ]
}
3. Preserve the logical order of steps and keep IDs unique.  
4. Do not include any extra keys or commentary—just the chosen topic’s JSON.  
"""
promptHuman = """
Generate a simple but realistic flowchart using the follow structure {seed_value}"""

def promptImage(flowChartInfo):
    promptImage = f"""
    Draw a clean, professional flowchart representing the {flowChartInfo["name"]} workflow described below.
    {flowChartInfo.model_dump_json(indent=2)}
    For each object in nodes:
        If "type": "start" or "end", draw a circle labeled with "label".
        If "type": "decision", draw a diamond labeled with "label".
        Otherwise (e.g. "type": "task"), draw a rectangle labeled with "label".
    For each object in edges:
        Draw an arrow from the shape with id="from" to the shape with id="to".
        If "condition" isn’t empty, place that text next to the arrow (e.g. “SI” or “NO”).
    Extra styling notes:
    All text in a clear, legible sans-serif font,
    Modes and arrows in black on white background.
    Uniform node sizing with padding around labels.
    Straight or gently curved lines; avoid overlap.
    Decision diamonds sized to accommodate two outgoing arrows clearly,
    with “SI” arrow going right or down-right, “NO” arrow going down or left.
    The overall layout should flow top-to-bottom, centered on the page,
    with consistent spacing between elements. 
    Use standard flowchart shapes:
    Start/End nodes as circles,
    Decision nodes as diamonds,
    Task nodes as rectangles,
    Arrows connecting nodes with arrowheads.
    Produce the diagram at high resolution so all labels are crisp and easily readable.
    """
    return promptImage

