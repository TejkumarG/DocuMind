import json
import os
from typing import List
from config.settings import settings


def store_feedback(question: str, context: List[str], answer: str, liked: bool = True):
    """
    Store user feedback (liked answers) to feedback.jsonl for future recompilation.

    Args:
        question: The user's question
        context: Context chunks used
        answer: The generated answer
        liked: Whether the user liked the answer (default True)
    """
    if not liked:
        # Only store liked answers
        return

    feedback_path = settings.feedback_path

    # Ensure directory exists
    os.makedirs(os.path.dirname(feedback_path), exist_ok=True)

    feedback_entry = {
        "question": question,
        "context": context,
        "answer": answer
    }

    # Append to JSONL file
    with open(feedback_path, "a") as f:
        f.write(json.dumps(feedback_entry) + "\n")

    print(f"Feedback stored to {feedback_path}")
