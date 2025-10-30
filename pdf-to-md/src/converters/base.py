"""
Base converter interface
"""
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """Abstract base class for PDF to Markdown converters"""

    @abstractmethod
    def convert(self, pdf_path: str, output_path: str) -> bool:
        """
        Convert PDF to Markdown

        Args:
            pdf_path: Path to input PDF
            output_path: Path to output markdown file

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get converter name"""
        pass
