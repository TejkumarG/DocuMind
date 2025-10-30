import json
import os
from typing import List, Dict
from config.settings import settings


def prepare_training_samples() -> List[Dict]:
    """
    Load training samples from training_samples.json.

    This function reads the gold training examples used for DSPy compilation.

    Returns:
        List of training samples with question, context, and answer
    """
    samples_path = settings.training_samples_path

    if not os.path.exists(samples_path):
        print(f"Warning: Training samples not found at {samples_path}")
        return []

    with open(samples_path, "r") as f:
        samples = json.load(f)

    print(f"Loaded {len(samples)} training samples from {samples_path}")
    return samples


def create_sample_training_data():
    """
    Create a sample training_samples.json file with example data.

    This is a helper function to bootstrap the training data.
    """
    samples_path = settings.training_samples_path

    # Ensure directory exists
    os.makedirs(os.path.dirname(samples_path), exist_ok=True)

    sample_data = [
        {
            "question": "Who founded Tesla Motors?",
            "context": [
                "Tesla Motors was founded by Martin Eberhard and Marc Tarpenning in 2003.",
                "Elon Musk joined the company as chairman in 2004.",
                "The company was named after inventor Nikola Tesla."
            ],
            "answer": "Tesla Motors was founded by Martin Eberhard and Marc Tarpenning in 2003."
        },
        {
            "question": "What is the capital of France?",
            "context": [
                "Paris is the capital and largest city of France.",
                "The city is located on the Seine River in northern France.",
                "Paris is known for the Eiffel Tower and the Louvre Museum."
            ],
            "answer": "The capital of France is Paris."
        }
        # Add 98 more samples to reach 100 total
    ]

    with open(samples_path, "w") as f:
        json.dump(sample_data, f, indent=2)

    print(f"Created sample training data at {samples_path}")
    print(f"Note: Only {len(sample_data)} samples created. Add more to reach 100.")


if __name__ == "__main__":
    # Create sample data if it doesn't exist
    if not os.path.exists(settings.training_samples_path):
        create_sample_training_data()
    else:
        samples = prepare_training_samples()
        print(f"Found {len(samples)} existing training samples")
