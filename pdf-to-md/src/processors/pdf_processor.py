"""
PDF processing orchestrator
"""
from pathlib import Path
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..detector import TableDetector
from ..converters.base import BaseConverter


class PDFProcessor:
    """Orchestrates PDF to Markdown conversion"""

    def __init__(
        self,
        detector: TableDetector,
        pymupdf_converter: BaseConverter,
        openai_converter: BaseConverter,
        logger=None,
        max_workers: int = 4
    ):
        """
        Initialize processor with dependency injection

        Args:
            detector: Table detector instance
            pymupdf_converter: PyMuPDF converter instance
            openai_converter: OpenAI converter instance
            logger: Logger instance (optional)
            max_workers: Maximum parallel workers (default: 4)
        """
        self.detector = detector
        self.converters = {
            "pymupdf": pymupdf_converter,
            "openai": openai_converter
        }
        self.logger = logger
        self.max_workers = max_workers

    def process_directory(
        self,
        input_dir: str,
        output_dir: str
    ) -> Dict[str, dict]:
        """
        Process all PDFs in directory

        Args:
            input_dir: Directory containing PDFs
            output_dir: Directory for markdown output

        Returns:
            Dictionary with processing results
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_path.glob("*.pdf"))

        if not pdf_files:
            if self.logger:
                self.logger.error(f"No PDF files found in {input_dir}")
            return {}

        if self.logger:
            self.logger.separator()
            self.logger.info(f"📂 Found {len(pdf_files)} PDF file(s)")
            self.logger.separator()
            self.logger.info("")

        # PHASE 1: Detect tables sequentially (avoids PyTorch conflicts)
        if self.logger:
            self.logger.info("🔍 Phase 1: Detecting tables...")
            self.logger.info("")

        detection_results = {}
        for pdf_file in pdf_files:
            pdf_path = str(pdf_file)
            if self.logger:
                self.logger.info(f"  Analyzing: {pdf_file.name}")

            try:
                has_tables, decision = self.detector.detect(pdf_path)
                detection_results[pdf_file.name] = {
                    "has_tables": has_tables,
                    "decision": decision,
                    "pdf_path": pdf_path,
                    "output_path": str(output_path / f"{pdf_file.stem}.md")
                }
                if self.logger:
                    self.logger.info(f"    → Tables: {has_tables} | Strategy: {decision.upper()}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"    → Detection failed: {e}")
                detection_results[pdf_file.name] = {
                    "has_tables": False,
                    "decision": "pymupdf",
                    "pdf_path": pdf_path,
                    "output_path": str(output_path / f"{pdf_file.stem}.md"),
                    "error": str(e)
                }

        # PHASE 2: Convert in parallel
        if self.logger:
            self.logger.info("")
            self.logger.info("🚀 Phase 2: Converting documents in parallel...")
            self.logger.separator()
            self.logger.info("")

        results = {}
        max_workers = min(self.max_workers, len(pdf_files))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit conversion tasks
            future_to_pdf = {
                executor.submit(
                    self._convert_file,
                    detection_results[pdf_file.name]
                ): pdf_file
                for pdf_file in pdf_files
            }

            # Collect results as they complete
            for future in as_completed(future_to_pdf):
                pdf_file = future_to_pdf[future]
                try:
                    result = future.result()
                    results[pdf_file.name] = result
                except Exception as e:
                    # Log error but continue with other PDFs
                    if self.logger:
                        self.logger.error(f"Unexpected error converting {pdf_file.name}: {e}")
                    results[pdf_file.name] = {
                        "has_tables": detection_results[pdf_file.name].get("has_tables", False),
                        "decision": detection_results[pdf_file.name].get("decision", "unknown"),
                        "converter": "N/A",
                        "success": False,
                        "output": None
                    }

        # Summary
        self._print_summary(results)

        return results

    def _convert_file(self, detection_info: dict) -> dict:
        """
        Convert a single PDF file (without detection)

        Args:
            detection_info: Dictionary with detection results and paths

        Returns:
            Dictionary with conversion result
        """
        pdf_path = detection_info["pdf_path"]
        output_path = detection_info["output_path"]
        has_tables = detection_info["has_tables"]
        decision = detection_info["decision"]
        pdf_name = Path(pdf_path).name

        if self.logger:
            self.logger.separator()
            self.logger.info(f"📄 Converting: {pdf_name}")
            self.logger.separator()
            self.logger.info(f"🎯 Strategy: {decision.upper()}")

        # Select converter
        converter = self.converters[decision]

        if self.logger:
            self.logger.info(f"⚙️  Using: {converter.get_name()}")
            self.logger.info("🔄 Converting...")

        # Convert
        success = converter.convert(pdf_path, output_path)

        if self.logger:
            if success:
                self.logger.success(f"✅ Success: {Path(output_path).name}\n")
            else:
                self.logger.error(f"❌ Failed\n")

        return {
            "has_tables": has_tables,
            "decision": decision,
            "converter": converter.get_name(),
            "success": success,
            "output": output_path if success else None
        }

    def process_file(self, pdf_path: str, output_path: str) -> dict:
        """
        Process single PDF file

        Args:
            pdf_path: Path to PDF file
            output_path: Path to output markdown file

        Returns:
            Dictionary with processing result
        """
        pdf_name = Path(pdf_path).name

        if self.logger:
            self.logger.separator()
            self.logger.info(f"📄 Processing: {pdf_name}")
            self.logger.separator()

            # Detect tables
            self.logger.info("🔍 Analyzing document...")

        has_tables, decision = self.detector.detect(pdf_path)

        if self.logger:
            self.logger.info(f"📊 Tables detected: {has_tables}")
            self.logger.info(f"🎯 Strategy: {decision.upper()}")
            self.logger.debug(f"PDF path: {pdf_path}")
            self.logger.debug(f"Output path: {output_path}")

        # Select converter
        converter = self.converters[decision]

        if self.logger:
            self.logger.info(f"⚙️  Using: {converter.get_name()}")

        # Convert
        if self.logger:
            self.logger.info("🔄 Converting...")

        success = converter.convert(pdf_path, output_path)

        if self.logger:
            if success:
                self.logger.success(f"Success: {Path(output_path).name}\n")
            else:
                self.logger.error(f"Failed\n")

        return {
            "has_tables": has_tables,
            "decision": decision,
            "converter": converter.get_name(),
            "success": success,
            "output": output_path if success else None
        }

    def _print_summary(self, results: Dict[str, dict]):
        """Print processing summary"""
        if not self.logger:
            return

        self.logger.info(f"\n{'#'*60}")
        self.logger.info("📋 PROCESSING SUMMARY")
        self.logger.info(f"{'#'*60}")

        total = len(results)
        successful = sum(1 for r in results.values() if r["success"])
        failed = total - successful

        for filename, result in results.items():
            status = "✅" if result["success"] else "❌"
            has_tables_str = "Yes" if result.get("has_tables", False) else "No"
            self.logger.info(f"{status} {filename}")
            self.logger.info(f"   Tables: {has_tables_str} | "
                  f"Converter: {result['converter']}")

        self.logger.info(f"\n{'─'*60}")
        self.logger.info(f"Total: {total} | Success: {successful} | Failed: {failed}")
        self.logger.info(f"{'#'*60}\n")
