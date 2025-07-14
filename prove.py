import re

def parse_score_and_text(response: str):
    pattern = r'^\s*(0(?:\.\d+)?|1(?:\.0+)?)\s+(.*)$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    score = float(m.group(1))
    text = m.group(2).strip()
    return score, text

# Test it:
response = "0.37 Here is the prompt generated"
score, prompt = parse_score_and_text(response)
print(type(score))  # 0.37
print(type(prompt)) # "Here is the prompt generated"
