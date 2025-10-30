"""
PyMuPDF4LLM-based PDF to Markdown converter
"""
from .base import BaseConverter
from pathlib import Path
import re


class PyMuPDFConverter(BaseConverter):
    """Converts PDFs using pymupdf4llm library"""

    def __init__(self, logger=None):
        """
        Initialize PyMuPDF converter

        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger

    def convert(self, pdf_path: str, output_path: str) -> bool:
        """
        Convert PDF to Markdown using pymupdf4llm

        Args:
            pdf_path: Path to input PDF
            output_path: Path to output markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            import pymupdf4llm
            from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders

            if self.logger:
                self.logger.debug("Converting with pymupdf4llm")

            # Convert PDF to markdown with header detection and page chunks
            hdr_info = IdentifyHeaders(pdf_path)
            chunks = pymupdf4llm.to_markdown(pdf_path, hdr_info=hdr_info, page_chunks=True)

            # Combine chunks with page number comments
            markdown_parts = []
            for chunk in chunks:
                page_num = chunk['metadata'].get('page', 'Unknown')
                page_text = chunk.get('text', '')

                # Add page comment and text
                markdown_parts.append(f"<!-- Page {page_num} -->\n\n{page_text}")

            markdown_content = "\n\n".join(markdown_parts)

            # Post-process to improve markdown formatting
            markdown_content = self._improve_markdown(markdown_content)

            # Write to file
            Path(output_path).write_text(markdown_content, encoding='utf-8')

            if self.logger:
                self.logger.debug(f"Wrote {len(markdown_content)} characters to {output_path}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"PyMuPDF conversion failed: {e}")
            return False

    def _improve_markdown(self, content: str) -> str:
        """
        Improve markdown formatting by converting bold headings to proper # headings
        and removing excessive bold markers

        Args:
            content: Raw markdown content

        Returns:
            Improved markdown content
        """
        lines = content.split('\n')
        improved_lines = []

        for line in lines:
            # Check if line is entirely bold (likely a heading)
            # Pattern: **word** **word** **word** (all bold, uppercase or title case)
            if line.strip() and re.match(r'^(\*\*[A-Z][^\*]*\*\*\s*)+$', line.strip()):
                # Remove all ** markers and convert to heading
                heading_text = re.sub(r'\*\*', '', line.strip())
                # Clean up extra spaces
                heading_text = re.sub(r'\s+', ' ', heading_text).strip()

                # Determine heading level (all caps = ## , title case = ###)
                if heading_text.isupper():
                    improved_lines.append(f"## {heading_text}")
                else:
                    improved_lines.append(f"### {heading_text}")
            else:
                # Remove all ** bold markers from regular lines
                cleaned_line = re.sub(r'\*\*', '', line)
                improved_lines.append(cleaned_line)

        return '\n'.join(improved_lines)

    def get_name(self) -> str:
        return "PyMuPDF4LLM"
