"""
Logging utility
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


class Logger:
    """Centralized logging utility"""

    def __init__(self, name: str = "pdf-converter", log_dir: str = "logs"):
        """
        Initialize logger

        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"conversion_{timestamp}.log"

        # File handler (detailed logs)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler (clean output)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Store log file path
        self.log_file = str(log_file)

        self.info(f"📝 Logging to: {log_file}")

    def debug(self, message: str):
        """Log debug message (file only)"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message (file + console)"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message (file + console)"""
        self.logger.warning(f"⚠️  {message}")

    def error(self, message: str):
        """Log error message (file + console)"""
        self.logger.error(f"❌ {message}")

    def success(self, message: str):
        """Log success message (file + console)"""
        self.logger.info(f"✅ {message}")

    def separator(self, char: str = "=", length: int = 60):
        """Log separator line"""
        self.info(char * length)

    def get_log_file(self) -> str:
        """Get current log file path"""
        return self.log_file
