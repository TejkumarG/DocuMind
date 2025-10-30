"""
Configuration settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    INPUT_DIR = DATA_DIR / "raw_docs"
    OUTPUT_DIR = DATA_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Table Detection
    TABLE_MIN_COLS = int(os.getenv("TABLE_MIN_COLS", "3"))
    TABLE_MIN_ROWS = int(os.getenv("TABLE_MIN_ROWS", "5"))
    TABLE_MIN_ACCURACY = float(os.getenv("TABLE_MIN_ACCURACY", "90.0"))
    TABLE_SCAN_PAGES = int(os.getenv("TABLE_SCAN_PAGES", "5"))

    # Parallel Processing
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))

    # OpenAI Chunking (Vision API)
    OPENAI_CHUNK_SIZE = int(os.getenv("OPENAI_CHUNK_SIZE", "5"))

    @classmethod
    def validate(cls):
        """Validate required settings"""
        # Only validate paths, not API keys (validate on-demand)
        if not cls.INPUT_DIR.exists():
            raise FileNotFoundError(f"Input directory not found: {cls.INPUT_DIR}")


# Create singleton instance
settings = Settings()
