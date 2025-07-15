
promptSystem = """
You are gonna to create a flowchart you are gonna to use this schema :
  "nodes": [
     "id": string, "type": "start" | "end" |
       "decision" | "task", "text": string , "x": int,
        "y": int,
        "width": int,
        "height": int
  ],
  "edges": [
     "from": string, "to": string, "label": string ,
     "fromSide": "bottom"| "top" | "left" | "rigth" , 
     "toSide" : ...
  ]
Instructions:
1. Identify Nodes
  - For each distinct step or state in the description, create one node object.
  - Assign `"id"` to a unique identifier (e.g. `"n1"`, `"n2"`, …).
   - Set `"type"` based on its role:"
     - `"start"` or `"end"` for the beginning or terminal steps,
     - `"decision"` for yes/no or branch points,
     - `"task"` for any other action or process.
   - Use `"text"` for the exact text shown in the flowchart. If it is long put a \n in the middle of the text.
   - Use `"x"` and `"y"` to position the figure in the xy plane. We read the flowchart from top to bottom, so `"y"` should
   to decrease, use numbers similar like the example that user is gonna to give you.
   - Use `"width"` and `"height"` to define the size of the rectangle or diamond or circle where text is gonna to be put,
   so if is a long text increase both, for better stetics.
2. Identify Edges
   - For each transition or arrow between steps, create one edge object.
   - Use `"from"` and `"to"` to reference the `id` of
   the source and destination nodes.
   - If the transition has a label (e.g. “YES”, “NO”, or any annotation),
    put it in `"label"`. Otherwise set `"label": ""`.
   - Use `"fromSide"` and `"toSide"` for the arrows end and start matching with "from" and "to", example
    like the flowchart is tipically top-to-bottom `"fromSide:bottom"` "`toSide:top"`.      
3. Ordering & Uniqueness
   - List nodes in the logical order they
    appear top‑to‑bottom or left‑to‑right.
   - List edges in the sequence they occur or in
   a consistent grouping by source node.
   - Ensure all `id` values are unique and referenced correctly.
Be precise with the logic and be simple, not more than ten nodes.
"""
promptHuman = """Generate a flowchart about {topic} using
the follow structure {seed_value}"""

promptTopicSys = "User wants to generate flowcharts and needs a topic, give one, be concise, no more than 30 words and no further explanations"
promptTopicHum = "Give me one topic for one flowchart"

def promptValidator(variant,threshold):
  prompt = f"""I generate a flowchart following the follow schema: {variant}; assign to the image a number between zero and one depending if the arrows are nice or not, if the score
  is greater than {threshold} then just return that number and "Any", otherwise create a prompt for modify only the arrows for better aesthetics I care more about the arrows from the diamonds.
  Just return those two anything else!
  Example: 0.1 Modify the arrow from node n1 to n2 , 0.9 Any, don't use quotation marks. 
  """
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
    Don't put a title on the image.
    And the background is a white color
    """
    return promptImage
