#!/usr/bin/env python3
"""
S2 Document Intelligence - CLI Tool
Batch process documents from command line
"""

import argparse
import json
from pathlib import Path
import uuid
import sys

from services.document_processor import process_pdf_to_layout_json


def process_folder(input_dir: Path, output_dir: Path, overwrite: bool = False, verbose: bool = False) -> None:
    """Process all PDFs in a folder"""
    output_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([p for p in input_dir.rglob("*.pdf") if p.is_file()])
    
    if not pdfs:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdfs)} PDF files")
    
    for i, pdf_path in enumerate(pdfs, 1):
        doc_id = uuid.uuid4().hex
        out_file = output_dir / f"{pdf_path.stem}_{doc_id}.json"
        
        if out_file.exists() and not overwrite:
            if verbose:
                print(f"[{i}/{len(pdfs)}] Skipping {pdf_path.name} (already processed)")
            continue
        
        try:
            if verbose:
                print(f"[{i}/{len(pdfs)}] Processing {pdf_path.name}...")
            
            result = process_pdf_to_layout_json(str(pdf_path), document_id=doc_id)
            out_file.write_text(result, encoding="utf-8")
            
            result_data = json.loads(result)
            num_pages = len(result_data.get("pages", []))
            
            print(json.dumps({
                "status": "success",
                "input": str(pdf_path),
                "output": str(out_file),
                "document_id": doc_id,
                "pages": num_pages
            }))
        
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "input": str(pdf_path),
                "error": str(e)
            }), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="S2 Document Intelligence - Batch process PDFs into layout JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in folder
  python cli.py input_folder/ output_folder/
  
  # Overwrite existing outputs
  python cli.py input_folder/ output_folder/ --overwrite
  
  # Verbose output
  python cli.py input_folder/ output_folder/ --verbose

For advanced features (mobile apps, web UI, advanced AI):
  Contact: beta@s2intelligence.com
  GitHub: https://github.com/s2artslab/s2-document-intelligence
        """
    )
    parser.add_argument("input", type=str, help="Input folder containing PDFs")
    parser.add_argument("output", type=str, help="Output folder for JSON files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    process_folder(input_dir, output_dir, overwrite=args.overwrite, verbose=args.verbose)


if __name__ == "__main__":
    main()
