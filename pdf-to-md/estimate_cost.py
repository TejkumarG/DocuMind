"""
Cost estimation script - analyzes PDFs and estimates OpenAI costs WITHOUT converting
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.detector import TableDetector
import pymupdf

load_dotenv()

def estimate_costs():
    """Estimate conversion costs for all PDFs"""
    detector = TableDetector()

    input_dir = "data/raw_docs"
    pdf_files = list(Path(input_dir).glob("*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        return

    print("="*60)
    print(f"📊 COST ESTIMATION FOR {len(pdf_files)} PDF(S)")
    print("="*60)
    print()

    # Track statistics
    total_pdfs = len(pdf_files)
    pymupdf_count = 0
    openai_count = 0
    total_pages_openai = 0

    results = []

    # Analyze each PDF
    for pdf_file in pdf_files:
        pdf_path = str(pdf_file)

        # Get page count
        doc = pymupdf.open(pdf_path)
        page_count = len(doc)
        doc.close()

        # Detect tables
        print(f"📄 {pdf_file.name}")
        print(f"   Pages: {page_count}")

        try:
            has_tables, decision = detector.detect(pdf_path)

            if decision == "openai":
                openai_count += 1
                total_pages_openai += page_count
                est_cost = page_count * 0.004  # $0.004 per page estimate
                print(f"   🔍 Tables: YES")
                print(f"   💰 Converter: OpenAI Vision API")
                print(f"   💵 Estimated cost: ${est_cost:.4f}")

                results.append({
                    "name": pdf_file.name,
                    "pages": page_count,
                    "converter": "OpenAI",
                    "cost": est_cost
                })
            else:
                pymupdf_count += 1
                print(f"   🔍 Tables: NO")
                print(f"   💰 Converter: PyMuPDF4LLM (FREE)")

                results.append({
                    "name": pdf_file.name,
                    "pages": page_count,
                    "converter": "PyMuPDF4LLM",
                    "cost": 0.0
                })
        except Exception as e:
            print(f"   ❌ Error analyzing: {e}")
            results.append({
                "name": pdf_file.name,
                "pages": page_count,
                "converter": "ERROR",
                "cost": 0.0
            })

        print()

    # Print summary
    total_cost = sum(r["cost"] for r in results)

    print("="*60)
    print("💰 COST SUMMARY")
    print("="*60)
    print(f"Total PDFs: {total_pdfs}")
    print(f"  • PyMuPDF4LLM (Free): {pymupdf_count} PDFs")
    print(f"  • OpenAI Vision API: {openai_count} PDFs ({total_pages_openai} pages)")
    print()
    print(f"Estimated OpenAI Cost: ${total_cost:.4f}")

    if total_cost > 0:
        print()
        print("💡 Cost Breakdown:")
        print(f"   • Input tokens: ~$0.15 per 1M tokens")
        print(f"   • Output tokens: ~$0.60 per 1M tokens")
        print(f"   • Average: ~$0.004 per page")
        print()
        print("📝 Note: Actual cost may vary by ±20% based on:")
        print("   - Image complexity")
        print("   - Table density")
        print("   - Text content")

    print("="*60)

    if openai_count > 0:
        print()
        print("❓ Ready to proceed with conversion?")
        print(f"   Estimated cost: ${total_cost:.4f}")
        print()
        print("Run: docker-compose run --rm pdf-converter")
    else:
        print()
        print("✅ All PDFs are simple documents - conversion is FREE!")
        print()
        print("Run: docker-compose run --rm pdf-converter")

if __name__ == "__main__":
    estimate_costs()
