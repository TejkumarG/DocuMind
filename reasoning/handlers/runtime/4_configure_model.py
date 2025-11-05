import dspy
from config.settings import settings


def configure_dspy_model():
    """
    Configure DSPy with OpenAI model for runtime inference.

    This sets up the LLM that will be used for Reason + Verify calls.

    Note: seed=None ensures no deterministic caching by OpenAI API
    """
    lm = dspy.OpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.openai_temperature,
        max_tokens=1000,  # Ensure complete responses (adjust as needed)
        seed=None,  # Disable deterministic responses/caching
    )

    dspy.settings.configure(lm=lm)

    return lm
