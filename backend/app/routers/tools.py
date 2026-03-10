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
from fastapi.background import BackgroundTasks

from app.services.merge_service import merge_pdfs_in_memory
from app.services.split_service import split_pdf_in_memory
from app.services.rotate_service import rotate_pdf_in_memory
from app.services.compress_service import compress_pdf_service
from app.services.repair_service import repair_pdf_service
from app.services.protect_service import protect_pdf_service
from app.services.unlock_service import unlock_pdf_service
from app.services.watermark_service import watermark_pdf_service
from app.services.redact_service import redact_pdf_service
from app.services.ocr_service import ocr_pdf_service
from app.services.add_page_numbers_service import add_page_numbers_in_memory
from app.services.crop_service import crop_pdf_in_memory
from app.services.pdf_to_word_service import pdf_to_word_in_memory
from app.services.word_to_pdf_service import word_to_pdf_service
from app.services.pdf_to_excel_service import pdf_to_excel_in_memory
from app.services.excel_to_pdf_service import excel_to_pdf_service
from app.services.ppt_to_pdf_service import ppt_to_pdf_service
from app.services.pdf_to_jpg_service import pdf_to_jpg_in_memory
from app.services.organize_service import get_pdf_previews_in_memory, organize_pdf_in_memory
from app.config import settings
from app.core.redis_client import pdf_queue, redis_conn
from rq.job import Job
# worker import removed from top-level to prevent API startup issues
from app.services.validation import (
    validate_pdf_uploads,
    validate_image_uploads,
    validate_docx_uploads,
    validate_excel_uploads,
    validate_ppt_uploads,
)

logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _prepare_job_dir(job_id: str, files: list[UploadFile]) -> list[Path]:
    """
    Creates storage/jobs/{job_id}/input/ and saves the uploaded files.
    Returns a list of local Path objects.
    """
    job_dir = settings.JOBS_STORAGE_DIR / job_id
    input_dir = job_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    for upload in files:
        # Sanitize filename
        safe_name = Path(upload.filename or "file").name
        dest = input_dir / f"{uuid.uuid4().hex}_{safe_name}"
        
        # Read and enforce limit
        content = await upload.read()
        if len(content) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File '{upload.filename}' exceeds {settings.MAX_FILE_SIZE_MB}MB limit."
            )
            
        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)
        saved_paths.append(dest)
        
    return saved_paths

def _get_filename(custom_name: str | None, default_name: str) -> str:
    """Helper to determine the download filename."""
    if custom_name and custom_name.strip():
        name = custom_name.strip()
        if not name.lower().endswith(".pdf") and default_name.lower().endswith(".pdf"):
            name += ".pdf"
        return name
    return default_name

# ═══════════════════════════════════════════════════════════════════════════════
# GENERIC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/tools", summary="List all available tools")
async def list_tools():
    # Only sending a truncated tools list here for brevity
    return {"tools": [
        {"id": "merge-pdf", "category": "Organize", "title": "Merge PDF", "description": "Combine multiple PDFs into one."},
        {"id": "compress-pdf", "category": "Optimize", "title": "Compress PDF", "description": "Reduce PDF file size without quality loss."},
        {"id": "images-to-pdf", "category": "Convert", "title": "Images to PDF", "description": "Combine JPG/PNG images into a PDF."},
        {"id": "pdf-to-word", "category": "Convert", "title": "PDF to Word", "description": "Convert PDF to editable Word document."},
        {"id": "pdf-to-excel", "category": "Convert", "title": "PDF to Excel", "description": "Convert PDF data into Excel spreadsheets."}
    ]}

# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY, OPTIMIZED TOOL ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_filename(provided: str, default: str) -> str:
    """Sanitize and return a safe filename with correct extension."""
    import re
    if not provided:
        return default
    
    # Strip invalid path characters
    clean_name = re.sub(r'[<>:"/\\|?*]', '', provided).strip()
    if not clean_name:
        return default
        
    # Ensure correct extension matching the default
    ext = default[default.rfind('.'):] if '.' in default else '.pdf'
    if not clean_name.lower().endswith(ext):
        clean_name += ext
        
    return clean_name

# ═══════════════════════════════════════════════════════════════════════════════
# JOB MANAGEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/jobs/{job_id}", summary="Get the status of a processing job")
async def get_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.meta.get('status', job.get_status())
        
        return {
            "job_id": job.get_id(),
            "status": status,
            "result_ready": status == "finished",
            "error": job.meta.get('error') if status == "failed" else None,
            "metadata": {
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
                "started_at": job.meta.get('started_at'),
                "completed_at": job.meta.get('completed_at'),
                "processing_time": job.meta.get('processing_time')
            }
        }
    except Exception as e:
        logger.error(f"Job fetch failed: {job_id} - {e}")
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

@router.get("/jobs/{job_id}/download", summary="Download the result of a finished job")
async def download_job_result(request: Request, job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        status = job.meta.get('status', job.get_status())
        
        if status != "finished":
            raise HTTPException(status_code=400, detail=f"Job is {status}, not finished.")
            
        result_path = job.meta.get("result_path")
        if not result_path or not Path(result_path).exists():
            logger.error(f"Result file missing for job {job_id}: {result_path}")
            raise HTTPException(status_code=404, detail="Output file not found on server.")
            
        download_name = _get_filename(request.query_params.get("filename"), "processed.pdf")
        
        return FileResponse(
            path=result_path,
            filename=download_name,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal error during file retrieval.")

# ═══════════════════════════════════════════════════════════════════════════════
# TOOLS ENDPOINTS (Converted to Async Jobs)
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
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, files)
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            merge_pdfs_in_memory,
            saved_paths,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("merge-pdf", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Merge enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Merge enqueue failed: {exc}")


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
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            split_pdf_in_memory,
            saved_paths[0],
            mode=mode,
            ranges_str=range,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("split-pdf", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Split enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Split enqueue failed: {exc}")


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
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            rotate_pdf_in_memory,
            saved_paths[0],
            angle_str=angle,
            apply_to=apply_to,
            range_str=range,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("rotate-pdf", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Rotate enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Rotate enqueue failed: {exc}")


@router.post("/tools/repair-pdf", summary="Repair a corrupted PDF file")
@limiter.limit("5/minute")
async def repair_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            repair_pdf_service,
            saved_paths[0],
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Repair enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Repair enqueue failed: {exc}")


@router.post("/tools/protect-pdf", summary="Protect a PDF file with a password")
@limiter.limit("10/minute")
async def protect_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    password: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not password:
        raise HTTPException(status_code=400, detail="A password is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            protect_pdf_service,
            saved_paths[0],
            password,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Protection enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Protection enqueue failed: {exc}")


@router.post("/tools/unlock-pdf", summary="Unlock a password-protected PDF file")
@limiter.limit("10/minute")
async def unlock_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    password: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not password:
        raise HTTPException(status_code=400, detail="A password is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            unlock_pdf_service,
            saved_paths[0],
            password,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Unlock enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Unlock enqueue failed: {exc}")


@router.post("/tools/watermark-pdf", summary="Apply a text watermark to a PDF document")
@limiter.limit("10/minute")
async def watermark_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    text: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Watermark text is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            watermark_pdf_service,
            saved_paths[0],
            text,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("watermark-pdf", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Watermarking enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Watermarking enqueue failed: {exc}")


@router.post("/tools/redact-pdf", summary="Permanently redact text from a PDF document")
@limiter.limit("10/minute")
async def redact_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    text: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Redaction text is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            redact_pdf_service,
            saved_paths[0],
            text,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("redact-pdf", 120)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Redaction enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Redaction enqueue failed: {exc}")


@router.post("/tools/ocr-pdf", summary="Convert scanned PDF to searchable PDF using OCR")
@limiter.limit("10/minute")
async def ocr_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            ocr_pdf_service,
            saved_paths[0],
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("ocr-pdf", 300)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"OCR enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"OCR enqueue failed: {exc}")


@router.post("/tools/compress-pdf", summary="Compress a PDF file")
@limiter.limit("10/minute")
async def compress_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    target_size_mb: float = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            compress_pdf_service,
            saved_paths[0],
            target_size_mb,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("compress-pdf", 90)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Compression enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Compression enqueue failed: {exc}")


@router.post("/tools/images-to-pdf", summary="Convert images to a PDF document")
@limiter.limit("5/minute")
async def images_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    orientation: str = Form("Portrait"),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required.")

    validate_image_uploads(files)
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, files)
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            images_to_pdf_service,
            saved_paths,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Images-to-PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# ADD PAGE NUMBERS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tools/add-page-numbers", summary="Add page numbers to a PDF")
@limiter.limit("10/minute")
async def add_page_numbers_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    position: str = Form("Bottom Center"),
    format: str = Form("1, 2, 3"),
    start_num: str = Form("1"),
    margin: str = Form("Medium"),
    font_size: str = Form("Medium"),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        # Convert start_num
        start_n = int(start_num) if start_num.isdigit() else 1

        # Map UI format string to backend format string
        fmt_map = {
            "1, 2, 3": "{n}",
            "Page 1": "Page {n}",
            "Page 1 of N": "Page {n} of {total}",
        }
        fmt_str = fmt_map.get(format, "{n}")

        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            add_page_numbers_in_memory,
            pdf_bytes=saved_paths[0],
            position=position,
            format_str=fmt_str,
            start_num=start_n,
            margin=margin,
            font_size=font_size,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Add Page Numbers enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Adding page numbers enqueue failed: {exc}")

# ═══════════════════════════════════════════════════════════════════════════════
# CROP PDF ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tools/crop-pdf", summary="Crop margins of a PDF document")
@limiter.limit("10/minute")
async def crop_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    top_m: float = Form(0.0),
    bottom_m: float = Form(0.0),
    left_m: float = Form(0.0),
    right_m: float = Form(0.0),
    unit: str = Form("Points"),
    apply_to: str = Form("All pages"),
    range: str = Form("")
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads(files)
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            crop_pdf_in_memory,
            saved_paths[0],
            top_m,
            bottom_m,
            left_m,
            right_m,
            unit,
            apply_to,
            range,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Crop PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Cropping PDF enqueue failed: {exc}")

# ═══════════════════════════════════════════════════════════════════════════════
# ORGANIZE PAGES ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/pdf-pages-preview", summary="Generate page previews for a PDF")
@limiter.limit("20/minute")
async def pdf_pages_preview_endpoint(
    request: Request,
    file: UploadFile = File(...),
):
    if not file:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([file])

    try:
        pdf_bytes = await _read_upload_in_memory(file)
        data = get_pdf_previews_in_memory(pdf_bytes)
        return JSONResponse(status_code=200, content=data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Preview generation failed")
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {exc}")

import json

@router.post("/tools/organize-pages", summary="Organize and extract specific pages from a PDF")
@limiter.limit("10/minute")
async def organize_pages_endpoint(
    request: Request,
    file: UploadFile = File(...),
    page_order: str = Form("[]"),  # Expecting JSON string array
):
    if not file:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([file])
    job_id = str(uuid.uuid4())

    try:
        order_array = json.loads(page_order)
        if not isinstance(order_array, list):
            raise ValueError("page_order must be a JSON array")
        
        saved_paths = await _prepare_job_dir(job_id, [file])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            organize_pdf_in_memory,
            saved_paths[0],
            order_array,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for page_order")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Organize PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Organizing PDF enqueue failed: {exc}")

# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD ENDPOINTS (Requiring Disk I/O)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/tools/pdf-to-word", summary="Convert a PDF to a Word document")
@limiter.limit("10/minute")
async def pdf_to_word_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            pdf_to_word_in_memory,
            saved_paths[0],
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"PDF-to-Word enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")

@router.post("/tools/pdf-to-excel", summary="Convert a PDF to an Excel spreadsheet")
@limiter.limit("10/minute")
async def pdf_to_excel_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            pdf_to_excel_in_memory,
            saved_paths[0],
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"PDF-to-Excel enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")

@router.post("/tools/excel-to-pdf", summary="Convert an Excel file to a PDF document")
@limiter.limit("10/minute")
async def excel_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="An Excel file is required.")

    validate_excel_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            excel_to_pdf_service,
            saved_paths[0],
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Excel-to-PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")

@router.post("/tools/pdf-to-jpg", summary="Convert a PDF pages into JPG images")
@limiter.limit("10/minute")
async def pdf_to_jpg_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
    quality: str = Form("Medium"),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            pdf_to_jpg_in_memory,
            saved_paths[0],
            quality,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"PDF-to-JPG enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")

@router.post("/tools/word-to-pdf", summary="Convert a DOCX or DOC file into a PDF document")
@limiter.limit("10/minute")
async def word_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A Word document is required.")

    validate_docx_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            word_to_pdf_service,
            saved_paths[0],
            files[0].filename,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Word-to-PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")

@router.post("/tools/ppt-to-pdf", summary="Convert a PPTX or PPT file into a PDF document")
@limiter.limit("10/minute")
async def ppt_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PowerPoint document is required.")

    validate_ppt_uploads([files[0]])
    job_id = str(uuid.uuid4())

    try:
        saved_paths = await _prepare_job_dir(job_id, [files[0]])
        
        from app.workers.worker import job_wrapper
        job = pdf_queue.enqueue(
            job_wrapper,
            ppt_to_pdf_service,
            saved_paths[0],
            files[0].filename,
            job_id=job_id,
            job_timeout=settings.TIMEOUTS.get("default", 60)
        )

        return JSONResponse(status_code=202, content={
            "job_id": job.get_id(),
            "status": "queued"
        })

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"PowerPoint-to-PDF enqueue failed for job {job_id}")
        raise HTTPException(status_code=500, detail=f"Conversion enqueue failed: {exc}")
