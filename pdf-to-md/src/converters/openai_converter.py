"""
OpenAI-based PDF to Markdown converter using Vision API
"""
from .base import BaseConverter
from pathlib import Path
import pymupdf
import base64
import io


class OpenAIConverter(BaseConverter):
    """Converts PDFs using OpenAI Vision API"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", logger=None, chunk_size: int = 5):
        """
        Initialize OpenAI converter

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini)
            logger: Logger instance (optional)
            chunk_size: Pages per chunk (default: 5 for Vision API)
        """
        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.chunk_size = chunk_size

    def convert(self, pdf_path: str, output_path: str) -> bool:
        """
        Convert PDF to Markdown using OpenAI Vision API (chunk-based)

        Args:
            pdf_path: Path to input PDF
            output_path: Path to output markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate API key before processing
            if not self.api_key or self.api_key.strip() == "":
                if self.logger:
                    self.logger.error("OpenAI API key not set - cannot use Vision API")
                    self.logger.error("Set OPENAI_API_KEY in .env file to use OpenAI conversion")
                return False

            from openai import OpenAI

            # Open PDF
            doc = pymupdf.open(pdf_path)
            total_pages = len(doc)

            if self.logger:
                self.logger.info(f"   📄 Total pages: {total_pages}")
                self.logger.info(f"   🔢 Processing in chunks of {self.chunk_size} pages")
                self.logger.info(f"   👁️  Using Vision API (auto detail mode)")

            # Calculate chunks
            chunks = []
            for start_page in range(0, total_pages, self.chunk_size):
                end_page = min(start_page + self.chunk_size, total_pages)
                chunks.append((start_page, end_page))

            if self.logger:
                self.logger.info(f"   📦 Total chunks: {len(chunks)}")

            # Process each chunk
            client = OpenAI(api_key=self.api_key)
            all_markdown = []
            total_tokens_in = 0
            total_tokens_out = 0

            for i, (start, end) in enumerate(chunks, 1):
                if self.logger:
                    self.logger.info(f"   🔄 Chunk {i}/{len(chunks)}: Pages {start+1}-{end}")

                # Convert pages to images
                images_content = []
                for page_num in range(start, end):
                    page = doc[page_num]

                    # Render page to image (PNG)
                    pix = page.get_pixmap(dpi=150)  # 150 DPI for good quality
                    img_bytes = pix.tobytes("png")

                    # Encode to base64
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')

                    images_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "auto"  # Auto detail mode for cost efficiency
                        }
                    })

                # Build message with all images in chunk
                # Generate page numbers for this chunk
                page_numbers = list(range(start+1, end+1))
                pages_list = ", ".join([f"Page {p}" for p in page_numbers])

                message_content = [
                    {
                        "type": "text",
                        "text": f"""Convert these PDF pages to clean, well-structured markdown.

You are processing {len(page_numbers)} page(s): {pages_list}
The images are provided in sequential order.

IMPORTANT - Page Number Format:
- Before converting each page's content, add EXACTLY this comment: <!-- Page N -->
- For example, if processing page 10, start with: <!-- Page 10 -->
- Then add a blank line, then the page content
- Repeat for each page

Requirements:
- Preserve ALL tables in markdown table format (| Column | Column |)
- Maintain document structure (headings, lists, sections)
- Keep all important information (no summarization)
- Maintain proper spacing between sections
- Process images in order: first image = {page_numbers[0]}, second image = {page_numbers[1] if len(page_numbers) > 1 else 'N/A'}, etc.

Example output structure:
<!-- Page 10 -->

[content of page 10]

<!-- Page 11 -->

[content of page 11]

Process all pages now."""
                    }
                ]
                message_content.extend(images_content)

                # Call OpenAI Vision API
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": message_content
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.1
                )

                chunk_markdown = response.choices[0].message.content
                all_markdown.append(chunk_markdown)

                # Track tokens
                usage = response.usage
                total_tokens_in += usage.prompt_tokens
                total_tokens_out += usage.completion_tokens

                if self.logger:
                    self.logger.debug(f"      Tokens: {usage.prompt_tokens} in, {usage.completion_tokens} out")

            # Close document
            doc.close()

            # Combine all chunks
            final_markdown = "\n\n".join(all_markdown)

            # Write to file
            Path(output_path).write_text(final_markdown, encoding='utf-8')

            # Calculate total cost
            total_cost = (total_tokens_in * 0.15 + total_tokens_out * 0.6) / 1_000_000

            if self.logger:
                self.logger.info(f"   📊 Total tokens: {total_tokens_in} in, {total_tokens_out} out")
                self.logger.info(f"   💰 Total cost: ${total_cost:.4f}")
                self.logger.debug(f"Wrote {len(final_markdown)} characters to {output_path}")

            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"OpenAI Vision conversion failed: {e}")
            return False

    def get_name(self) -> str:
        return f"OpenAI ({self.model})"
