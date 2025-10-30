from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.0

    # DSPy Configuration
    compiled_model_path: str = "artifacts/compiled_rag_v1.dspy"
    training_samples_path: str = "data/training_samples.json"
    feedback_path: str = "data/feedback.jsonl"

    # Training Configuration
    num_training_samples: int = 100
    compile_batch_size: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
