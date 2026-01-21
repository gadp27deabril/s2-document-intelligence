"""
S2 Document Intelligence - Community Edition
Core document processing API

This is the open-source version with core features.
For advanced features (mobile apps, web UI, etc), see Premium Edition.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional
import uuid
import shutil
import os
import logging

from services.document_processor import process_pdf_to_layout_json, process_image_to_layout_json

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="S2 Document Intelligence - Community Edition",
    version="1.0.0",
    description="Open-source document processing API with OCR and layout analysis",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "S2 Document Intelligence",
        "version": "1.0.0",
        "edition": "Community (Open Source)",
        "description": "Document processing API with OCR and layout analysis",
        "docs": "/docs",
        "github": "https://github.com/s2artslab/s2-document-intelligence",
        "premium": "For mobile apps, web UI, and advanced features, contact beta@s2intelligence.com"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "edition": "community"}

@app.post("/process/pdf")
async def process_pdf(
    file: UploadFile = File(...),
    enable_ocr: bool = Form(True),
    ocr_lang: str = Form("en"),
):
    """
    Process a PDF document
    
    Parameters:
    - file: PDF file to process
    - enable_ocr: Enable OCR for scanned documents (default: True)
    - ocr_lang: OCR language code (default: "en")
    
    Returns:
    - JSON with document structure, text, and layout
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file
    doc_id = uuid.uuid4().hex
    file_path = UPLOAD_DIR / f"{doc_id}.pdf"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing PDF: {file.filename} (id: {doc_id})")
        
        # Process document
        result = process_pdf_to_layout_json(
            str(file_path),
            document_id=doc_id,
            enable_ocr=enable_ocr,
            ocr_lang=ocr_lang
        )
        
        # Clean up uploaded file
        file_path.unlink()
        
        return JSONResponse(content={"success": True, "data": result})
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/process/image")
async def process_image(
    file: UploadFile = File(...),
    ocr_lang: str = Form("en"),
):
    """
    Process an image with OCR
    
    Parameters:
    - file: Image file (jpg, png, etc.)
    - ocr_lang: OCR language code (default: "en")
    
    Returns:
    - JSON with OCR results and layout
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail=f"File must be an image ({', '.join(allowed_extensions)})")
    
    # Save uploaded file
    doc_id = uuid.uuid4().hex
    file_ext = Path(file.filename).suffix
    file_path = UPLOAD_DIR / f"{doc_id}{file_ext}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing image: {file.filename} (id: {doc_id})")
        
        # Process image
        result = process_image_to_layout_json(
            str(file_path),
            document_id=doc_id,
            ocr_lang=ocr_lang
        )
        
        # Clean up uploaded file
        file_path.unlink()
        
        return JSONResponse(content={"success": True, "data": result})
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting S2 Document Intelligence - Community Edition")
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"API Docs: http://{host}:{port}/docs")
    logger.info(f"For Premium features (mobile apps, web UI, advanced AI), visit: https://s2intelligence.com")
    
    uvicorn.run(app, host=host, port=port)
