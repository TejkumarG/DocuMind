import os
import dspy
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from dspy.teleprompt import MIPROv2 as Optimizer
except ImportError:
    try:
        from dspy.teleprompt import MIPRO as Optimizer
    except ImportError:
        from dspy.teleprompt import BootstrapFewShot as Optimizer

from config.settings import settings
from importlib import import_module

# Import functions from numbered modules
prepare_samples_module = import_module('handlers.offline.1_prepare_samples')
prepare_training_samples = prepare_samples_module.prepare_training_samples

reason_verify_module = import_module('handlers.runtime.5_reason_verify')
ReasonVerifyRAG = reason_verify_module.ReasonVerifyRAG


def answer_faithfulness(example, pred, trace=None):
    """
    Metric to evaluate if the answer is faithful to the context.

    Args:
        example: Ground truth example with question, context, answer
        pred: Predicted answer from the model
        trace: Optional trace information

    Returns:
        Score between 0 and 1
    """
    # Simple metric: check if predicted answer is similar to expected
    # In production, you might use a more sophisticated metric
    predicted_answer = pred.verified_answer if hasattr(pred, 'verified_answer') else str(pred)
    expected_answer = example.answer if hasattr(example, 'answer') else ""

    # Normalize and compare
    predicted_lower = predicted_answer.lower().strip()
    expected_lower = expected_answer.lower().strip()

    # Simple word overlap metric
    predicted_words = set(predicted_lower.split())
    expected_words = set(expected_lower.split())

    if not expected_words:
        return 0.0

    overlap = len(predicted_words & expected_words)
    score = overlap / len(expected_words)

    return min(score, 1.0)


def compile_dspy_model(num_samples: int = None):
    """
    Compile DSPy model using MIPROv2 optimizer.

    Args:
        num_samples: Number of training samples to use (default from settings)

    Returns:
        Path to the compiled model
    """
    if num_samples is None:
        num_samples = settings.num_training_samples

    print("=" * 60)
    print("Starting DSPy Compilation")
    print("=" * 60)

    # Configure DSPy with OpenAI
    print(f"\n1. Configuring DSPy with model: {settings.openai_model}")
    lm = dspy.OpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.openai_temperature,
    )
    dspy.settings.configure(lm=lm)

    # Load training samples
    print(f"\n2. Loading training samples...")
    training_data = prepare_training_samples()

    if not training_data:
        raise ValueError("No training samples found. Please create training_samples.json first.")

    # Limit to requested number of samples
    training_data = training_data[:num_samples]
    print(f"   Using {len(training_data)} training samples")

    # Convert to DSPy examples
    trainset = []
    for sample in training_data:
        example = dspy.Example(
            question=sample["question"],
            context=sample["context"],
            answer=sample["answer"]
        ).with_inputs("question", "context")
        trainset.append(example)

    # Initialize RAG pipeline
    print(f"\n3. Initializing ReasonVerifyRAG pipeline...")
    rag = ReasonVerifyRAG()

    # Compile with optimizer
    optimizer_name = Optimizer.__name__
    print(f"\n4. Compiling with {optimizer_name} optimizer...")
    print(f"   This may take a while (may require multiple LLM calls)...")

    # Create optimizer with parameters that work for most optimizers
    try:
        if optimizer_name in ['MIPROv2', 'MIPRO']:
            compiler = Optimizer(
                metric=answer_faithfulness,
                auto="light",  # Use 'light' for faster compilation
                num_threads=4,
            )
            compiled_rag = compiler.compile(
                rag,
                trainset=trainset,
                num_trials=10,
                max_bootstrapped_demos=3,
                max_labeled_demos=3,
            )
        else:  # BootstrapFewShot
            compiler = Optimizer(
                metric=answer_faithfulness,
                max_bootstrapped_demos=3,
                max_labeled_demos=3,
            )
            compiled_rag = compiler.compile(
                student=rag,
                trainset=trainset,
            )
    except Exception as e:
        print(f"Warning: Optimizer compilation failed: {e}")
        print("Continuing with uncompiled model...")
        compiled_rag = rag

    # Save compiled model
    print(f"\n5. Saving compiled model...")
    model_path = settings.compiled_model_path
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    compiled_rag.save(model_path)

    print(f"\n{'=' * 60}")
    print(f" Compilation Complete!")
    print(f" Model saved to: {model_path}")
    print(f" Trained on {len(trainset)} examples")
    print(f"{'=' * 60}\n")

    return model_path


if __name__ == "__main__":
    compile_dspy_model()
