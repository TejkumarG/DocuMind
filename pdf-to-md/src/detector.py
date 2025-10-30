"""
Table detection module for PDFs using vision-based approach
"""
import warnings
warnings.filterwarnings('ignore')

from typing import Dict, Tuple
from pdf2image import convert_from_path
from PIL import Image
import torch
from transformers import pipeline


class TableDetector:
    """Detects tables in PDF documents using vision transformer model"""

    def __init__(self):
        """Initialize table detector with vision model"""
        self.model_name = "microsoft/table-transformer-detection"
        self.device = 0 if torch.cuda.is_available() else -1
        self.detector = None  # Lazy load on first use

    def detect(self, pdf_path: str, max_pages: int = 5) -> Tuple[bool, str]:
        """
        Detect if PDF has tables using vision-based approach

        Strategy:
        1. Convert PDF pages to images
        2. Use Microsoft table-transformer-detection model (DETR-based)
        3. Early exit on first table found
        4. No false positives from multi-column text layouts

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to scan

        Returns:
            Tuple of (has_tables, decision)
            has_tables: bool - True if ANY table found
            decision: "openai" or "pymupdf"
        """
        result = self._has_tables_vision(pdf_path, max_pages)

        has_tables = result["has_tables"]
        decision = "openai" if has_tables else "pymupdf"

        return has_tables, decision

    def _has_tables_vision(self, pdf_path: str, max_pages: int = 5,
                           dpi: int = 200, conf_threshold: float = 0.90) -> Dict:
        """
        Detects tables using vision transformer model on first N pages.
        Early-exits on first positive hit.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum pages to scan
            dpi: Resolution for PDF to image conversion
            conf_threshold: Confidence threshold for table detection (0.0-1.0)

        Returns:
            {
                "has_tables": bool,
                "pages_with_tables": [int, ...],   # 1-based
                "detections": {
                    page_num: [{"score": float, "bbox": [x1,y1,x2,y2], "label": str}, ...]
                },
                "device": "cuda|cpu",
                "model": "microsoft/table-transformer-detection"
            }
        """
        out = {
            "has_tables": False,
            "pages_with_tables": [],
            "detections": {},
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "model": self.model_name,
        }

        # 1) Render only the first N pages as images (fast, and stops early if possible)
        try:
            pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=max_pages)
        except Exception as e:
            # If PDF conversion fails, return no tables detected
            out["error"] = str(e)
            return out

        # 2) Load detector once (lazy loading)
        if self.detector is None:
            try:
                self.detector = pipeline(
                    task="object-detection",
                    model=self.model_name,
                    device=self.device
                )
            except Exception as e:
                out["error"] = f"Failed to load model: {str(e)}"
                return out

        # 3) Infer page-by-page with early exit
        #    Use autocast on GPU for speed; keep a strict confidence threshold.
        autocast = torch.cuda.amp.autocast if out["device"] == "cuda" else torch.cpu.amp.autocast

        for idx, pil_img in enumerate(pages, start=1):
            # Optional: downscale very large pages to cap inference cost
            MAX_W = 1800
            if pil_img.width > MAX_W:
                ratio = MAX_W / pil_img.width
                pil_img = pil_img.resize((MAX_W, int(pil_img.height * ratio)), Image.BILINEAR)

            try:
                with autocast():
                    preds = self.detector(pil_img)

                # Keep only 'table' with score >= threshold
                keep = []
                for p in preds:
                    if p.get("label", "").lower() == "table" and p.get("score", 0.0) >= conf_threshold:
                        # Normalize bbox to [x1,y1,x2,y2] in pixel space
                        b = p.get("box", {})
                        keep.append({
                            "score": float(p.get("score", 0.0)),
                            "bbox": [float(b.get("xmin", 0)), float(b.get("ymin", 0)),
                                   float(b.get("xmax", 0)), float(b.get("ymax", 0))],
                            "label": p.get("label", "")
                        })

                out["detections"][idx] = keep
                if keep:
                    out["has_tables"] = True
                    out["pages_with_tables"].append(idx)
                    # Early exit on first positive page
                    return out
            except Exception as e:
                # If inference fails on this page, continue to next
                out["detections"][idx] = []
                continue

        return out
