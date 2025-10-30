from typing import List, Dict, Any
import os
import logging
from pathlib import Path
import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load documents and split them by pages"""

    @staticmethod
    def load_pdf(file_path: str) -> List[Dict[str, Any]]:
        """Load PDF and return list of pages with metadata"""
        pages = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                document_id = Path(file_path).stem

                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    if text.strip():  # Only add non-empty pages
                        pages.append({
                            "document_id": document_id,
                            "page_number": page_num,
                            "text": text.strip(),
                            "file_path": file_path
                        })

                logger.info(f"Loaded {len(pages)} pages from PDF: {file_path}")
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            raise

        return pages

    @staticmethod
    def load_markdown(file_path: str) -> List[Dict[str, Any]]:
        """Load markdown file and split by page markers"""
        pages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                document_id = Path(file_path).stem

                # Split by page markers (<!-- Page N -->)
                import re
                page_pattern = r'<!--\s*Page\s+(\d+)\s*-->'
                page_splits = re.split(page_pattern, content)

                # If no page markers found, treat entire file as one page
                if len(page_splits) == 1:
                    if content.strip():
                        pages.append({
                            "document_id": document_id,
                            "page_number": 1,
                            "text": content.strip(),
                            "file_path": file_path
                        })
                else:
                    # Process each page
                    # page_splits format: [content_before_first_page, page_num_1, page_content_1, page_num_2, page_content_2, ...]
                    for i in range(1, len(page_splits), 2):
                        if i + 1 < len(page_splits):
                            page_num = int(page_splits[i])
                            page_text = page_splits[i + 1].strip()

                            if page_text:
                                pages.append({
                                    "document_id": document_id,
                                    "page_number": page_num,
                                    "text": page_text,
                                    "file_path": file_path
                                })

                logger.info(f"Loaded {len(pages)} pages from markdown file: {file_path}")
        except Exception as e:
            logger.error(f"Error loading markdown {file_path}: {e}")
            raise

        return pages

    @staticmethod
    def load_document(file_path: str) -> List[Dict[str, Any]]:
        """Load document based on file extension"""
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            return DocumentLoader.load_pdf(file_path)
        elif ext in ['.md', '.markdown', '.txt']:
            return DocumentLoader.load_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def load_directory(directory_path: str) -> List[Dict[str, Any]]:
        """Load all supported documents from a directory"""
        all_pages = []
        supported_extensions = {'.pdf', '.md', '.markdown', '.txt'}

        for root, _, files in os.walk(directory_path):
            for file in files:
                if Path(file).suffix.lower() in supported_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        pages = DocumentLoader.load_document(file_path)
                        all_pages.extend(pages)
                    except Exception as e:
                        logger.error(f"Failed to load {file_path}: {e}")

        logger.info(f"Loaded total {len(all_pages)} pages from directory: {directory_path}")
        return all_pages
