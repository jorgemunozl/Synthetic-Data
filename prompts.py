
promptSystem = """You are FlowTopicJSONBot.

2. Then, **output only** the flowchart’s JSON in this schema :
  "nodes": [
     "id": string, "type": "start" | "end" |
       "decision" | "task", "label": string ,
    …
  ],
  "edges": [
     "from": string, "to": string, "label": string ,
    …
  ]
Instructions:
1. **Identify Nodes**
  - For each distinct step or state in the description, create one node object.
  - Assign `"id"` to a unique identifier (e.g. `"n1"`, `"n2"`, …).
   - Set `"type"` based on its role:
     - `"start"` or `"end"` for the beginning or terminal steps,
     - `"decision"` for yes/no or branch points,
     - `"task"` for any other action or process.
   - Use `"label"` for the exact text shown in the flowchart.
2. **Identify Edges**
   - For each transition or arrow between steps, create one edge object.
   - Use `"from"` and `"to"` to reference the `id` of
   the source and destination nodes.
   - If the transition has a label (e.g. “YES”, “NO”, or any annotation),
    put it in `"label"`. Otherwise set `"label": ""`.
3. **Ordering & Uniqueness**
   - List nodes in the logical order they
    appear top‑to‑bottom or left‑to‑right.
   - List edges in the sequence they occur or in
   a consistent grouping by source node.
   - Ensure all `id` values are unique and referenced correctly.

4. Be precise because after you create the JSON we are gonna to create
images from these, for that reason is quite necesary that you are making
a precise and acurately flowcharts.
"""
promptHuman = """Generate a flowchart about {topic} using
the follow sstructure {seed_value}"""
promptTopicSys = "User wants to generate a ton of flowcharts, give some interesting ideas, be concise, no more than 30 words"
promptTopicHum = "Give me one topic for one flowchart"

def prompValidator(variant,threshold):
  prompt = f"""This is what I want {variant}, assign to the image a number between zero and one, if the score
  is greater than {threshold} then just return that number, otherwise create a prompt for tweak the image. Just return those two anything else!"""
  return prompt

def promptImage(flowChartInfo):
    promptImage = f"""
    Draw a clean, professional flowchart representing
    the {flowChartInfo["name"]} workflow described below:
    {flowChartInfo}
    For each object in nodes:
      If "type": "start" or "end", draw a circle labeled with "label".
      If "type": "decision", draw a diamond labeled with "label".
      Otherwise (e.g. "type": "task"), draw a rectangle labeled with "label".
    For each object in edges:
    Draw an arrow from the shape with id="from" to the shape with id="to".
    If "condition" isn’t empty, place that text
    next to the arrow (e.g. “YES” or “NO”).
    Extra styling notes:
    All text in a clear, legible sans-serif font,
    Uniform node sizing with padding around labels.
    Straight or gently curved lines; avoid overlap.
    with “YES” arrow going right or down-right, “NO” arrow going down or left.
    The overall layout should flow top-to-bottom, centered on the page,
    with consistent spacing between elements.
    Arrows connecting nodes with arrowheads.
    Produce the diagram at high resolution so all
    labels are crisp and easily readable.
    Don't put a title on the image
    """
    return promptImage
