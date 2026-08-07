from typing import List, Dict, Any, Optional

from app.llm.llm_client import chat_completion
from app.utils.llm_json import parse_json_response
from app.config import JUDGE_MODEL

JUDGE_SYSTEM_PROMPT = """You are an evaluation judge for a RAG system's answers.
Score the answer on three dimensions, each an integer 1-5:
- correctness: is the answer factually correct given the retrieved context (and reference answer if provided)?
- groundedness: is every claim in the answer supported by the retrieved chunks (no hallucination)?
- completeness: does the answer fully address the question?

Respond with ONLY valid JSON, no other text, no markdown fences:
{"correctness": 1-5, "groundedness": 1-5, "completeness": 1-5, "notes": "1-2 sentences explaining the scores"}
"""


def score_answer(
    question: str,
    answer: str,
    chunks: List[Dict[str, Any]],
    reference_answer: Optional[str] = None,
) -> Dict[str, Any]:
    context = "\n\n".join(
        f"[Chunk {c.get('chunk_id', i)}]: {c['content']}" for i, c in enumerate(chunks)
    ) or "(no chunks were retrieved)"

    user_content = f"QUESTION: {question}\n\nRETRIEVED CONTEXT:\n{context}\n\nGENERATED ANSWER: {answer}"
    if reference_answer:
        user_content += f"\n\nREFERENCE ANSWER: {reference_answer}"

    raw = chat_completion(
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        model=JUDGE_MODEL,
        json_mode=True,
        temperature=0,
    )
    result = parse_json_response(raw)
    result["overall"] = round(
        (result["correctness"] + result["groundedness"] + result["completeness"]) / 3, 2
    )
    return result
