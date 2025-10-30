import dspy
from config.settings import settings


def configure_dspy_model():
    """
    Configure DSPy with OpenAI model for runtime inference.

    This sets up the LLM that will be used for Reason + Verify calls.
    """
    lm = dspy.OpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.openai_temperature,
    )

    dspy.settings.configure(lm=lm)

    return lm
