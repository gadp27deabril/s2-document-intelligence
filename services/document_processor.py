"""
Core document processing engine
Extracts text, layout, and structure from PDFs and images
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import logging

# PyMuPDF for PDF processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    fitz = None
    PYMUPDF_AVAILABLE = False

# OCR engines (optional)
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PaddleOCR = None
    PADDLE_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    easyocr = None
    EASYOCR_AVAILABLE = False

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Global OCR instances (lazy init)
_paddle_ocr = None
_easy_ocr = None


def _get_paddle_ocr():
    """Get or initialize PaddleOCR"""
    global _paddle_ocr
    if _paddle_ocr is None and PADDLE_AVAILABLE:
        _paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    return _paddle_ocr


def _get_easy_ocr(lang='en'):
    """Get or initialize EasyOCR"""
    global _easy_ocr
    if _easy_ocr is None and EASYOCR_AVAILABLE:
        _easy_ocr = easyocr.Reader([lang], gpu=True)
    return _easy_ocr


def process_pdf_to_layout_json(
    pdf_path: str,
    document_id: str = None,
    enable_ocr: bool = True,
    ocr_lang: str = "en"
) -> str:
    """
    Process PDF and return layout JSON
    
    Args:
        pdf_path: Path to PDF file
        document_id: Optional document ID
        enable_ocr: Enable OCR for scanned documents
        ocr_lang: OCR language code
    
    Returns:
        JSON string with document structure
    """
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (fitz) is required for PDF processing. Install with: pip install PyMuPDF")
    
    doc_id = document_id or Path(pdf_path).stem
    
    try:
        pdf_doc = fitz.open(pdf_path)
        pages = []
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            width, height = int(page.rect.width), int(page.rect.height)
            
            # Extract text blocks
            blocks = []
            raw_blocks = page.get_text("blocks")
            
            for i, blk in enumerate(raw_blocks):
                if len(blk) < 5:
                    continue
                x0, y0, x1, y1, text = blk[:5]
                text_str = text if isinstance(text, str) else str(text)
                clean_lines = [ln.strip() for ln in text_str.splitlines() if ln.strip()]
                
                if clean_lines:
                    blocks.append({
                        "id": f"b{i+1}",
                        "role": "text",
                        "bbox": [int(x0), int(y0), int(x1), int(y1)],
                        "text": "\n".join(clean_lines),
                        "confidence": 1.0
                    })
            
            # OCR if no text found
            if enable_ocr and len(blocks) == 0:
                logger.info(f"No text found on page {page_num + 1}, trying OCR...")
                ocr_blocks = _ocr_page(page, ocr_lang)
                if ocr_blocks:
                    blocks = ocr_blocks
            
            # Sort blocks by reading order
            blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
            
            pages.append({
                "page": page_num + 1,
                "width": width,
                "height": height,
                "blocks": blocks
            })
        
        pdf_doc.close()
        
        result = {
            "document_id": doc_id,
            "filename": Path(pdf_path).name,
            "num_pages": len(pages),
            "pages": pages
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        raise


def _ocr_page(page, lang: str = "en") -> List[Dict]:
    """Run OCR on a PDF page"""
    try:
        # Render page to image
        pix = page.get_pixmap(dpi=300)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        if pix.n == 4:  # RGBA
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        elif pix.n == 1:  # Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
        # Try PaddleOCR first (faster)
        if PADDLE_AVAILABLE:
            paddle = _get_paddle_ocr()
            if paddle:
                result = paddle.ocr(img, cls=True)
                if result and result[0]:
                    blocks = []
                    for i, line in enumerate(result[0]):
                        bbox_points, (text, conf) = line
                        xs = [p[0] for p in bbox_points]
                        ys = [p[1] for p in bbox_points]
                        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                        
                        blocks.append({
                            "id": f"ocr{i+1}",
                            "role": "text",
                            "bbox": [x0, y0, x1, y1],
                            "text": text,
                            "confidence": float(conf)
                        })
                    return blocks
        
        # Fallback to EasyOCR
        if EASYOCR_AVAILABLE:
            easy = _get_easy_ocr(lang)
            if easy:
                result = easy.readtext(img)
                blocks = []
                for i, (bbox, text, conf) in enumerate(result):
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                    
                    blocks.append({
                        "id": f"ocr{i+1}",
                        "role": "text",
                        "bbox": [x0, y0, x1, y1],
                        "text": text,
                        "confidence": float(conf)
                    })
                return blocks
        
        logger.warning("No OCR engines available (install paddleocr or easyocr)")
        return []
    
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return []


def process_image_to_layout_json(
    image_path: str,
    document_id: str = None,
    ocr_lang: str = "en"
) -> str:
    """
    Process image with OCR and return layout JSON
    
    Args:
        image_path: Path to image file
        document_id: Optional document ID
        ocr_lang: OCR language code
    
    Returns:
        JSON string with OCR results
    """
    doc_id = document_id or Path(image_path).stem
    
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        height, width = img.shape[:2]
        
        # Run OCR
        blocks = []
        
        # Try PaddleOCR first
        if PADDLE_AVAILABLE:
            paddle = _get_paddle_ocr()
            if paddle:
                result = paddle.ocr(img, cls=True)
                if result and result[0]:
                    for i, line in enumerate(result[0]):
                        bbox_points, (text, conf) = line
                        xs = [p[0] for p in bbox_points]
                        ys = [p[1] for p in bbox_points]
                        x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                        
                        blocks.append({
                            "id": f"ocr{i+1}",
                            "role": "text",
                            "bbox": [x0, y0, x1, y1],
                            "text": text,
                            "confidence": float(conf)
                        })
        
        # Fallback to EasyOCR
        if not blocks and EASYOCR_AVAILABLE:
            easy = _get_easy_ocr(ocr_lang)
            if easy:
                result = easy.readtext(img)
                for i, (bbox, text, conf) in enumerate(result):
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                    
                    blocks.append({
                        "id": f"ocr{i+1}",
                        "role": "text",
                        "bbox": [x0, y0, x1, y1],
                        "text": text,
                        "confidence": float(conf)
                    })
        
        if not blocks:
            logger.warning("No OCR engines available or no text detected")
        
        # Sort by reading order
        blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        
        result = {
            "document_id": doc_id,
            "filename": Path(image_path).name,
            "num_pages": 1,
            "pages": [{
                "page": 1,
                "width": width,
                "height": height,
                "blocks": blocks
            }]
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        raise
