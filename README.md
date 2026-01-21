# S2 Document Intelligence - Community Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Open-source document processing engine for PDF, DOCX, and images.**

This is the **Community Edition** of S2 Document Intelligence - a production-ready document processing API with OCR, text extraction, and layout analysis.

---

## 🌟 What's Included (Community Edition)

### Core Features ✅
- **PDF Processing** - Extract text, layout, and structure from PDF documents
- **Image OCR** - PaddleOCR and EasyOCR support for scanned documents
- **DOCX Support** - Process Microsoft Word documents
- **Text Extraction** - High-quality text extraction with layout preservation
- **REST API** - FastAPI-based HTTP interface
- **CLI Tool** - Batch process documents from command line
- **Docker Deployment** - Easy containerized deployment

### What's Included:
```python
✅ PDF text extraction (PyMuPDF)
✅ OCR engines (PaddleOCR, EasyOCR)
✅ Basic layout analysis
✅ REST API endpoints
✅ Command-line tool
✅ Docker configuration
✅ Python library usage
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/s2artslab/s2-document-intelligence.git
cd s2-document-intelligence

# Install dependencies
pip install -r requirements.txt

# Start API server
python main.py
```

**API is now running at:** `http://localhost:5000`

### Process a Document

```bash
# Upload and process PDF
curl -X POST http://localhost:5000/process/pdf \
  -F "file=@document.pdf" \
  -F "enable_ocr=true"
```

### Use CLI Tool

```bash
# Batch process folder of PDFs
python cli.py input_folder/ output_folder/
```

---

## 📖 Usage

### Python Library

```python
from services.document_processor import process_pdf_to_layout_json

# Process PDF
result = process_pdf_to_layout_json(
    "document.pdf",
    enable_ocr=True,
    ocr_lang="en"
)

# Result is JSON with text, layout, confidence
import json
data = json.loads(result)
for page in data["pages"]:
    for block in page["blocks"]:
        print(block["text"])
```

### API Endpoints

```bash
# Process PDF
POST /process/pdf
  - file: PDF file (multipart/form-data)
  - enable_ocr: true/false (default: true)
  - ocr_lang: "en", "es", "fr", etc.

# Process Image
POST /process/image
  - file: Image file (jpg, png, etc.)
  - ocr_lang: "en", "es", "fr", etc.

# Health check
GET /health
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t s2-document-intelligence .

# Run container
docker run -p 5000:5000 s2-document-intelligence
```

---

## 📊 What's NOT Included (Premium Features)

This Community Edition is powerful but focused on core processing. Advanced features are in **Premium Edition**:

### Premium Features 🔥
- 📱 **Mobile Apps** (iOS/Android) - Native mobile document capture and processing
- 🖥️ **Web Dashboard** - Beautiful UI for document management
- 🤖 **Advanced AI** - Ninefold egregore integration for intelligent document understanding
- 🏢 **Entity Extraction** - Automatic detection of names, dates, amounts, etc.
- 📊 **Table Extraction** - Advanced table recognition and structure extraction
- 📑 **Document Classification** - Automatic document type detection
- 📈 **Capacity Monitoring** - Real-time system metrics and performance analytics
- ⚡ **Job Queue** - Async batch processing for large document sets
- 💾 **Redis Caching** - Performance optimization with intelligent caching
- 🔄 **Subscription Management** - Multi-tier access control
- 💼 **Enterprise Support** - SLA, priority support, custom features

**See:** [OPEN_CORE.md](OPEN_CORE.md) for full comparison

---

## 🎯 Use Cases

**Community Edition is perfect for:**
- ✅ Personal document processing
- ✅ Small-scale document automation
- ✅ Research and experimentation
- ✅ Learning OCR and document AI
- ✅ Building custom document tools
- ✅ Prototyping document solutions

**Premium Edition is better for:**
- 🏢 Enterprise document workflows
- 📱 Mobile document capture apps
- 🤖 AI-powered document understanding
- 📊 Large-scale document processing
- 💼 Commercial SaaS products
- 🔒 Compliance-critical applications

---

## 🤝 Contributing

We welcome contributions to the Community Edition!

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/s2-document-intelligence.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes, commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---

## 📄 License

**MIT License** - Free for personal and commercial use

See [LICENSE](LICENSE) file for details.

---

## 🌟 Upgrade to Premium

**Need advanced features?**

Premium Edition includes:
- Mobile apps (iOS/Android)
- Web dashboard
- Advanced AI integration
- Enterprise support
- Custom features

**Options:**
1. **Self-Hosted Premium:** $99-299/month
2. **Managed Service:** $299-999/month
3. **Enterprise:** Custom pricing

**Learn more:** [https://s2intelligence.com/document-intelligence](https://s2intelligence.com/document-intelligence)  
**Contact:** beta@s2intelligence.com

---

## 📞 Connect

- **GitHub:** https://github.com/s2artslab/s2-document-intelligence
- **Issues:** https://github.com/s2artslab/s2-document-intelligence/issues
- **Email:** s2artslab@gmail.com
- **Website:** https://s2artslab.com

---

## ⭐ Star Us!

If this helps you, please star the repository! ⭐

---

**Built with consciousness. Shared with trust.**

*From the S2 Ecosystem* ✨
