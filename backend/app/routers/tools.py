import os
import uuid
import logging
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.services.merge_service import merge_pdfs
from app.services.compress_service import compress_pdf
from app.services.image_to_pdf_service import images_to_pdf
from app.services.pdf_to_word_service import pdf_to_word

logger = logging.getLogger(__name__)

# ── Directory setup ──────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

router = APIRouter()


# ── Shared helpers ────────────────────────────────────────────────────────────

async def _save_upload(upload: UploadFile) -> Path:
    """Persist an UploadFile to UPLOAD_DIR and return its path."""
    ext  = Path(upload.filename or "file").suffix or ".bin"
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(await upload.read())
    return path


def _cleanup(*paths) -> None:
    """Best-effort deletion of temporary files."""
    for p in paths:
        try:
            os.remove(p)
        except Exception:
            pass


# ── Generic upload endpoint (kept for UploadBox compatibility) ────────────────

@router.post("/upload", summary="Upload a file for processing")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    path = await _save_upload(file)
    size = path.stat().st_size

    return JSONResponse(status_code=200, content={
        "status": "success",
        "original_filename": file.filename,
        "saved_as": path.name,
        "size_bytes": size,
    })


# ── Tool list ─────────────────────────────────────────────────────────────────

@router.get("/tools", summary="List all available tools")
async def list_tools():
    tools = [
        {"id": "merge-pdf",        "category": "Organize", "title": "Merge PDF",        "description": "Combine multiple PDFs into one."},
        {"id": "split-pdf",        "category": "Organize", "title": "Split PDF",        "description": "Extract pages or split into multiple files."},
        {"id": "rotate-pdf",       "category": "Organize", "title": "Rotate PDF",       "description": "Rotate pages to the correct orientation."},
        {"id": "organize-pages",   "category": "Organize", "title": "Organize Pages",   "description": "Reorder, delete or arrange PDF pages."},
        {"id": "add-page-numbers", "category": "Organize", "title": "Add Page Numbers", "description": "Stamp page numbers on your PDF."},
        {"id": "crop-pdf",         "category": "Organize", "title": "Crop PDF",         "description": "Crop pages to a custom size."},
        {"id": "pdf-to-word",      "category": "Convert",  "title": "PDF to Word",      "description": "Convert PDF to editable Word document."},
        {"id": "pdf-to-excel",     "category": "Convert",  "title": "PDF to Excel",     "description": "Extract PDF tables into a spreadsheet."},
        {"id": "pdf-to-jpg",       "category": "Convert",  "title": "PDF to JPG",       "description": "Convert PDF pages to JPG images."},
        {"id": "word-to-pdf",      "category": "Convert",  "title": "Word to PDF",      "description": "Convert Word documents to PDF."},
        {"id": "images-to-pdf",    "category": "Convert",  "title": "Images to PDF",    "description": "Combine JPG/PNG images into a PDF."},
        {"id": "compress-pdf",     "category": "Optimize", "title": "Compress PDF",     "description": "Reduce PDF file size without quality loss."},
        {"id": "repair-pdf",       "category": "Optimize", "title": "Repair PDF",       "description": "Fix corrupted or damaged PDF files."},
        {"id": "protect-pdf",      "category": "Security", "title": "Protect PDF",      "description": "Add password protection to your PDF."},
        {"id": "unlock-pdf",       "category": "Security", "title": "Unlock PDF",       "description": "Remove password from a PDF."},
        {"id": "watermark-pdf",    "category": "Security", "title": "Watermark PDF",    "description": "Add text or image watermark to PDF."},
        {"id": "redact-pdf",       "category": "Security", "title": "Redact PDF",       "description": "Permanently remove sensitive content."},
        {"id": "ocr-pdf",          "category": "Advanced", "title": "OCR PDF",          "description": "Make scanned PDFs searchable with OCR."},
        {"id": "compare-pdf",      "category": "Advanced", "title": "Compare PDF",      "description": "Highlight differences between two PDFs."},
        {"id": "scan-to-pdf",      "category": "Advanced", "title": "Scan to PDF",      "description": "Capture and convert scans to PDF."},
        {"id": "translate-pdf",    "category": "Advanced", "title": "Translate PDF",    "description": "Translate PDF content to another language."},
    ]
    return {"tools": tools}


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Merge PDF ─────────────────────────────────────────────────────────────────

@router.post("/tools/merge-pdf", summary="Merge multiple PDF files into one")
async def merge_pdf_endpoint(files: list[UploadFile] = File(...)):
    """
    Accepts 1+ PDF uploads and returns a single merged PDF.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required.")

    saved = []
    output_path = None

    try:
        for upload in files:
            saved.append(await _save_upload(upload))

        input_paths = [str(p) for p in saved]
        output_path = merge_pdfs(input_paths, str(OUTPUT_DIR))

        return FileResponse(
            path=output_path,
            filename="merged.pdf",
            media_type="application/pdf",
        )

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        logger.exception("Merge failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        _cleanup(*saved)


# ── Compress PDF ──────────────────────────────────────────────────────────────

@router.post("/tools/compress-pdf", summary="Compress a PDF file")
async def compress_pdf_endpoint(
    files: list[UploadFile] = File(...),
    quality: str = Form("Recommended"),
):
    """
    Accepts a single PDF and a quality level, returns a compressed PDF.
    """
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    upload = files[0]
    saved = None
    output_path = None

    try:
        saved = await _save_upload(upload)
        output_path = compress_pdf(str(saved), str(OUTPUT_DIR), quality=quality)

        return FileResponse(
            path=output_path,
            filename="compressed.pdf",
            media_type="application/pdf",
        )

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        logger.exception("Compression failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if saved:
            _cleanup(saved)


# ── Images to PDF ─────────────────────────────────────────────────────────────

@router.post("/tools/images-to-pdf", summary="Convert images to a PDF document")
async def images_to_pdf_endpoint(
    files: list[UploadFile] = File(...),
    orientation: str = Form("Portrait"),
):
    """
    Accepts 1+ images (JPG, PNG, WEBP) and returns a combined PDF.
    """
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required.")

    saved = []
    output_path = None

    try:
        for upload in files:
            saved.append(await _save_upload(upload))

        image_paths = [str(p) for p in saved]
        output_path = images_to_pdf(image_paths, str(OUTPUT_DIR), orientation=orientation)

        return FileResponse(
            path=output_path,
            filename="images.pdf",
            media_type="application/pdf",
        )

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        logger.exception("Images-to-PDF failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        _cleanup(*saved)


# ── PDF to Word ───────────────────────────────────────────────────────────────

@router.post("/tools/pdf-to-word", summary="Convert a PDF to a Word document")
async def pdf_to_word_endpoint(files: list[UploadFile] = File(...)):
    """
    Accepts a single PDF and returns a .docx file.
    """
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    upload = files[0]
    saved = None
    output_path = None

    try:
        saved = await _save_upload(upload)
        output_path = pdf_to_word(str(saved), str(OUTPUT_DIR))

        return FileResponse(
            path=output_path,
            filename="converted.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        logger.exception("PDF-to-Word conversion failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if saved:
            _cleanup(saved)
