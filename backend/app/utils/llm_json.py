import json
import re


def parse_json_response(raw: str) -> dict:
    """Strip markdown code fences (models sometimes add them despite
    instructions not to) and parse the result as JSON."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned.strip())
