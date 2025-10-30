"""
PDF to Markdown Converter
Main entry point
"""
from config.settings import settings
from src.utils.logger import Logger
from src.detector import TableDetector
from src.converters.pymupdf_converter import PyMuPDFConverter
from src.converters.openai_converter import OpenAIConverter
from src.processors.pdf_processor import PDFProcessor


def main():
    """Main execution function"""
    logger = None
    try:
        # Initialize logger
        logger = Logger(log_dir=str(settings.LOGS_DIR))

        # Validate settings
        settings.validate()

        # Initialize components (Dependency Injection)
        detector = TableDetector()

        pymupdf_converter = PyMuPDFConverter(logger=logger)

        openai_converter = OpenAIConverter(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            logger=logger,
            chunk_size=settings.OPENAI_CHUNK_SIZE
        )

        # Initialize processor
        processor = PDFProcessor(
            detector=detector,
            pymupdf_converter=pymupdf_converter,
            openai_converter=openai_converter,
            logger=logger,
            max_workers=settings.MAX_WORKERS
        )

        # Process all PDFs
        processor.process_directory(
            input_dir=str(settings.INPUT_DIR),
            output_dir=str(settings.OUTPUT_DIR)
        )

        logger.info(f"\n✅ All done! Check logs: {logger.get_log_file()}")

    except Exception as e:
        if logger:
            logger.error(f"ERROR: {e}")
        else:
            print(f"\n❌ ERROR: {e}\n")
        exit(1)


if __name__ == "__main__":
    main()
