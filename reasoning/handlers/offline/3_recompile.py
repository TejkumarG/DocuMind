import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import settings
from importlib import import_module

# Import compile function from numbered module
compile_module = import_module('handlers.offline.2_compile_dspy')
compile_dspy_model = compile_module.compile_dspy_model


def merge_feedback_into_training():
    """
    Merge feedback.jsonl into training_samples.json for recompilation.

    This function reads liked answers from feedback and adds them to
    the training set for improved model performance.

    Returns:
        Number of new samples added
    """
    feedback_path = settings.feedback_path
    training_path = settings.training_samples_path

    if not os.path.exists(feedback_path):
        print(f"No feedback file found at {feedback_path}")
        return 0

    # Load existing training samples
    if os.path.exists(training_path):
        with open(training_path, "r") as f:
            training_samples = json.load(f)
    else:
        training_samples = []

    # Load feedback
    feedback_samples = []
    with open(feedback_path, "r") as f:
        for line in f:
            if line.strip():
                feedback_samples.append(json.loads(line))

    print(f"Found {len(feedback_samples)} feedback samples")

    # Add feedback to training samples (avoid duplicates)
    existing_questions = {s["question"] for s in training_samples}
    new_count = 0

    for fb in feedback_samples:
        if fb["question"] not in existing_questions:
            training_samples.append({
                "question": fb["question"],
                "context": fb["context"],
                "answer": fb["answer"]
            })
            existing_questions.add(fb["question"])
            new_count += 1

    # Save updated training samples
    os.makedirs(os.path.dirname(training_path), exist_ok=True)
    with open(training_path, "w") as f:
        json.dump(training_samples, f, indent=2)

    print(f"Added {new_count} new samples to training data")
    print(f"Total training samples: {len(training_samples)}")

    return new_count


def recompile_with_feedback():
    """
    Recompile DSPy model with feedback data merged into training samples.

    Returns:
        Path to the new compiled model
    """
    print("=" * 60)
    print("Recompiling DSPy Model with Feedback")
    print("=" * 60)

    # Merge feedback
    new_samples = merge_feedback_into_training()

    if new_samples == 0:
        print("\nWarning: No new feedback samples found.")
        print("Proceeding with existing training data...")

    # Compile with updated data
    model_path = compile_dspy_model()

    return model_path


if __name__ == "__main__":
    recompile_with_feedback()
