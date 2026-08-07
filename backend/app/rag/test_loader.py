"""
Seed manufactured bad Q&A pairs across each failure category, run them
through the diagnostic agent, and print out the categorization so you can
sanity-check the prompt before relying on organic failures (which are slower
to accumulate and harder to control for a demo).

Run with:
    python -m app.rag.test_loader
"""
from app.diagnostics.diagnostic_agent import diagnose

MANUFACTURED_CASES = [
    {
        "label": "RETRIEVAL_MISS",
        "question": "What's the cancellation policy for enterprise plans?",
        "chunks": [
            {"chunk_id": 1, "source": "pricing_faq.md",
             "content": "Standard plans can be modified or discontinued at any time through the billing dashboard."},
            {"chunk_id": 2, "source": "pricing_faq.md",
             "content": "For questions about your plan, contact your account manager."},
        ],
        "answer": "You can modify or discontinue your plan at any time through the billing dashboard. "
                  "For further questions, contact your account manager.",
        "feedback_note": "This doesn't mention the 90-day notice period for enterprise contracts specifically.",
    },
    {
        "label": "CHUNKING_PROBLEM",
        "question": "What is the maximum file upload size on the Pro plan?",
        "chunks": [
            {"chunk_id": 5, "source": "limits.md", "content": "Plan limits table:\nPlan | Storage | Max Upload"},
            {"chunk_id": 6, "source": "limits.md", "content": "Pro | 500GB | 2GB per file"},
        ],
        "answer": "I don't see a specific maximum file upload size mentioned in the documentation.",
        "feedback_note": "The max upload size (2GB) is right there, it's just split from its table header.",
    },
    {
        "label": "AMBIGUOUS_QUERY",
        "question": "How do I reset it?",
        "chunks": [
            {"chunk_id": 9, "source": "faq.md",
             "content": "To reset your account password, go to Settings > Security > Reset Password."},
        ],
        "answer": "Go to Settings > Security > Reset Password to reset your password.",
        "feedback_note": "I meant reset my API key, not my password.",
    },
    {
        "label": "GENERATION_ERROR",
        "question": "Is the default API rate limit 100 or 1000 requests per minute?",
        "chunks": [
            {"chunk_id": 12, "source": "api_docs.md",
             "content": "The default API rate limit is 1000 requests per minute per API key."},
        ],
        "answer": "The default API rate limit is 100 requests per minute.",
        "feedback_note": "The chunk clearly says 1000, not 100 — the answer contradicts its own source.",
    },
    {
        "label": "NO_INFORMATION",
        "question": "Do you offer a discount for registered non-profits?",
        "chunks": [
            {"chunk_id": 15, "source": "pricing_faq.md",
             "content": "We offer monthly and annual billing cycles, with a 15% discount for annual billing."},
        ],
        "answer": "I don't see information about non-profit discounts in the documentation I have access to.",
        "feedback_note": None,
    },
]


def run():
    correct = 0
    for case in MANUFACTURED_CASES:
        print(f"\n=== expecting {case['label']} ===")
        result = diagnose(
            question=case["question"],
            chunks=case["chunks"],
            answer=case["answer"],
            feedback_note=case["feedback_note"],
        )
        got = result["failure_category"]
        match = "OK " if got == case["label"] else "MISMATCH"
        correct += got == case["label"]

        print(f"question:        {case['question']}")
        print(f"expected:        {case['label']}")
        print(f"got:             {got}  [{match}]")
        print(f"fix_type:        {result['proposed_fix']['fix_type']}")
        print(f"confidence:      {result['diagnosis_confidence']}")

    print(f"\n{correct}/{len(MANUFACTURED_CASES)} categorized as expected")


if __name__ == "__main__":
    run()
