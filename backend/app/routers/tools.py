import os
import io
import uuid
import logging
import aiofiles
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.merge_service import merge_pdfs_in_memory
from app.services.split_service import split_pdf_in_memory
from app.services.rotate_service import rotate_pdf_in_memory
from app.services.compress_service import compress_pdf_in_memory
from app.services.image_to_pdf_service import images_to_pdf_in_memory
from app.services.pdf_to_word_service import pdf_to_word
from app.config import settings
from app.services.validation import (
    validate_pdf_uploads,
    validate_image_uploads,
)

logger = logging.getLogger(__name__)

# ── Directories ───────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _read_upload_in_memory(upload: UploadFile) -> bytes:
    """
    Read the upload stream into memory, enforcing the 50 MB size limit.
    """
    content = await upload.read()
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File '{upload.filename}' is {len(content)/(1024*1024):.1f} MB — "
                f"maximum allowed size is {settings.MAX_FILE_SIZE_MB} MB."
            ),
        )
    return content

async def _save_upload(upload: UploadFile) -> Path:
    """Fallback for endpoints still requiring disk writes (e.g., pdf2docx)."""
    ext  = Path(upload.filename or "file").suffix.lower() or ".bin"
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    content = await _read_upload_in_memory(upload)
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)
    return path

def _cleanup(*paths) -> None:
    for p in paths:
        try:
            os.remove(p)
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# GENERIC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

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

@router.get("/tools", summary="List all available tools")
async def list_tools():
    # Only sending a truncated tools list here for brevity
    return {"tools": [
        {"id": "merge-pdf", "category": "Organize", "title": "Merge PDF", "description": "Combine multiple PDFs into one."},
        {"id": "compress-pdf", "category": "Optimize", "title": "Compress PDF", "description": "Reduce PDF file size without quality loss."},
        {"id": "images-to-pdf", "category": "Convert", "title": "Images to PDF", "description": "Combine JPG/PNG images into a PDF."},
        {"id": "pdf-to-word", "category": "Convert", "title": "PDF to Word", "description": "Convert PDF to editable Word document."}
    ]}

# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY, OPTIMIZED TOOL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tools/merge-pdf", summary="Merge multiple PDF files into one")
@limiter.limit("10/minute")
async def merge_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required.")

    validate_pdf_uploads(files)

    try:
        pdf_bytes_list = []
        for upload in files:
            pdf_bytes_list.append(await _read_upload_in_memory(upload))

        result_io = merge_pdfs_in_memory(pdf_bytes_list)

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="merged.pdf"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Merge failed")
        raise HTTPException(status_code=500, detail=f"Merge failed: {exc}")


@router.post("/tools/split-pdf", summary="Split a PDF file into multiple files or extract pages")
@limiter.limit("10/minute")
async def split_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    mode: str = Form("Split every page"),
    range: str = Form(""),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        result_io, media_type, filename = split_pdf_in_memory(pdf_bytes, mode=mode, ranges_str=range)

        return StreamingResponse(
            result_io,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Split failed")
        raise HTTPException(status_code=500, detail=f"Splitting failed: {exc}")


@router.post("/tools/rotate-pdf", summary="Rotate a PDF file")
@limiter.limit("10/minute")
async def rotate_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    angle: str = Form("90° clockwise"),
    apply_to: str = Form("All pages"),
    range: str = Form(""),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        result_io = rotate_pdf_in_memory(
            pdf_bytes, 
            angle_str=angle, 
            apply_to=apply_to, 
            range_str=range
        )

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="rotated.pdf"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Rotate failed")
        raise HTTPException(status_code=500, detail=f"Rotation failed: {exc}")




@router.post("/tools/compress-pdf", summary="Compress a PDF file")
@limiter.limit("10/minute")
async def compress_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    quality: str = Form("Recommended"),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        result_io = compress_pdf_in_memory(pdf_bytes, quality=quality)

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="compressed.pdf"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Compression failed")
        raise HTTPException(status_code=500, detail=f"Compression failed: {exc}")


@router.post("/tools/images-to-pdf", summary="Convert images to a PDF document")
@limiter.limit("10/minute")
async def images_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    orientation: str = Form("Portrait"),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required.")

    validate_image_uploads(files)

    try:
        image_bytes_list = []
        for upload in files:
            image_bytes_list.append(await _read_upload_in_memory(upload))

        result_io = images_to_pdf_in_memory(image_bytes_list, orientation=orientation)

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="images.pdf"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Images-to-PDF failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD ENDPOINTS (Requiring Disk I/O)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tools/pdf-to-word", summary="Convert a PDF to a Word document")
@limiter.limit("10/minute")
async def pdf_to_word_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    """
    pdf2docx uses disk files heavily. Left as FileResponse workflow.
    """
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    saved = []
    try:
        saved.append(await _save_upload(files[0]))
        output_path = pdf_to_word(str(saved[0]), str(OUTPUT_DIR))
        return FileResponse(
            path=output_path,
            filename="converted.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("PDF-to-Word failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")
    finally:
        _cleanup(*saved)
