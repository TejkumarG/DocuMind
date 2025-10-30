"""
Docling-based PDF to Markdown converter
"""
from .base import BaseConverter
from pathlib import Path
from typing import Optional


class DoclingConverter(BaseConverter):
    """Converts PDFs using Docling library"""

    def __init__(self, logger=None):
        """
        Initialize Docling converter

        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger

    def convert(self, pdf_path: str, output_path: str) -> bool:
        """
        Convert PDF to Markdown using Docling

        Args:
            pdf_path: Path to input PDF
            output_path: Path to output markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            from docling.document_converter import DocumentConverter

            if self.logger:
                self.logger.debug("Initializing Docling converter")

            converter = DocumentConverter()
            result = converter.convert(pdf_path)

            # Export to markdown with page numbers
            markdown_content = self._add_page_numbers(result.document)

            # Write to file
            Path(output_path).write_text(markdown_content, encoding='utf-8')

            if self.logger:
                self.logger.debug(f"Wrote {len(markdown_content)} characters to {output_path}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Docling conversion failed: {e}")
            return False

    def _add_page_numbers(self, document) -> str:
        """
        Add page number markers to markdown content

        Args:
            document: Docling document object

        Returns:
            Markdown string with page number comments
        """
        try:
            # Try to get page-by-page content
            pages_content = []

            # Iterate through pages if available
            for page_num, page in enumerate(document.pages, start=1):
                page_md = page.export_to_markdown()
                pages_content.append(f"<!-- Page {page_num} -->\n\n{page_md}")

            return "\n\n".join(pages_content)

        except (AttributeError, TypeError):
            # Fallback: if page iteration not available, just export normally
            # and add a single page comment
            markdown = document.export_to_markdown()
            return f"<!-- Page 1 -->\n\n{markdown}"

    def get_name(self) -> str:
        return "Docling"
