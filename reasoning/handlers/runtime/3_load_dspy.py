import os
import dspy
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import settings
from importlib import import_module


def load_compiled_dspy():
    """
    Load the compiled DSPy model if it exists, otherwise return a new instance.

    Returns:
        ReasonVerifyRAG instance (compiled or fresh)
    """
    model_path = settings.compiled_model_path

    if os.path.exists(model_path):
        print(f"Loading compiled DSPy model from {model_path}")
        try:
            rag = dspy.load(model_path)
            return rag
        except Exception as e:
            print(f"Error loading compiled model: {e}")
            print("Falling back to uncompiled RAG pipeline")
            # Import the ReasonVerifyRAG class dynamically
            reason_verify_module = import_module('handlers.runtime.5_reason_verify')
            return reason_verify_module.ReasonVerifyRAG()
    else:
        print(f"No compiled model found at {model_path}")
        print("Using uncompiled ReasonVerifyRAG pipeline")
        # Import the ReasonVerifyRAG class dynamically
        reason_verify_module = import_module('handlers.runtime.5_reason_verify')
        return reason_verify_module.ReasonVerifyRAG()
