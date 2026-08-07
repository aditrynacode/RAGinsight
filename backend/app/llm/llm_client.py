from typing import List, Dict, Optional
from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, CHAT_MODEL

_client: Optional[genai.Client] = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def chat_completion(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    """Same signature as the old OpenAI-backed version, so callers
    (query_service, diagnostic_agent, evaluator) don't need to change.
    Gemini takes the system prompt separately from the user content, so we
    split the OpenAI-style messages list into system_instruction + a single
    combined prompt.
    """
    client = get_client()

    system_instruction = None
    user_parts = []
    for m in messages:
        if m["role"] == "system":
            system_instruction = m["content"]
        else:
            user_parts.append(m["content"])
    prompt = "\n\n".join(user_parts)

    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )
    if json_mode:
        config.response_mime_type = "application/json"

    response = client.models.generate_content(
        model=model or CHAT_MODEL,
        contents=prompt,
        config=config,
    )
    return response.text
