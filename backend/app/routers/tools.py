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
from app.services.validation import (
    validate_pdf_uploads,
    validate_image_uploads,
    validate_docx_uploads,
    validate_excel_uploads,
    validate_ppt_uploads,
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
    import shutil
    from pathlib import Path
    for p in paths:
        try:
            path = Path(p)
            if path.exists():
                if path.is_file() or path.is_symlink():
                    path.unlink(missing_ok=True)
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
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

        download_name = _get_filename(request.query_params.get("filename"), "merged.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
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

        download_name = _get_filename(request.query_params.get("filename"), filename)

        return StreamingResponse(
            result_io,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
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

        download_name = _get_filename(request.query_params.get("filename"), "rotated.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Rotate failed")
        raise HTTPException(status_code=500, detail=f"Rotation failed: {exc}")




@router.post("/tools/repair-pdf", summary="Repair a corrupted PDF file")
@limiter.limit("5/minute")
async def repair_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        from starlette.concurrency import run_in_threadpool
        
        result_io, temp_dir = await run_in_threadpool(
            repair_pdf_service,
            pdf_bytes,
        )

        if temp_dir:
            background_tasks.add_task(_cleanup, temp_dir)

        download_name = _get_filename(request.query_params.get("filename"), "repaired.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Repair failed")
        raise HTTPException(status_code=500, detail=f"Repair failed: {exc}")


@router.post("/tools/protect-pdf", summary="Protect a PDF file with a password")
@limiter.limit("10/minute")
async def protect_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    password: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not password:
        raise HTTPException(status_code=400, detail="A password is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        from starlette.concurrency import run_in_threadpool
        
        result_io, temp_dir = await run_in_threadpool(
            protect_pdf_service,
            pdf_bytes,
            password
        )

        if temp_dir:
            background_tasks.add_task(_cleanup, temp_dir)

        download_name = _get_filename(request.query_params.get("filename"), "protected.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Protection failed")
        raise HTTPException(status_code=500, detail=f"Protection failed: {exc}")


@router.post("/tools/unlock-pdf", summary="Unlock a password-protected PDF file")
@limiter.limit("10/minute")
async def unlock_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    password: str = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")
        
    if not password:
        raise HTTPException(status_code=400, detail="A password is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        from starlette.concurrency import run_in_threadpool
        
        result_io, temp_dir = await run_in_threadpool(
            unlock_pdf_service,
            pdf_bytes,
            password
        )

        if temp_dir:
            background_tasks.add_task(_cleanup, temp_dir)

        download_name = _get_filename(request.query_params.get("filename"), "unlocked.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Unlock failed")
        raise HTTPException(status_code=500, detail=f"Unlock failed: {exc}")


@router.post("/tools/compress-pdf", summary="Compress a PDF file")
@limiter.limit("10/minute")
async def compress_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    target_size_mb: float = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        from starlette.concurrency import run_in_threadpool
        
        result_io, temp_dir = await run_in_threadpool(
            compress_pdf_service,
            pdf_bytes,
            target_size_mb
        )

        if temp_dir:
            background_tasks.add_task(_cleanup, temp_dir)

        download_name = _get_filename(request.query_params.get("filename"), "compressed.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
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
        import time
        start_time = time.time()
        
        image_bytes_list = []
        for upload in files:
            image_bytes_list.append(await _read_upload_in_memory(upload))
            
        read_time = time.time() - start_time
        logger.info(f"Images to PDF: Read {len(files)} files in {read_time:.3f}s")
        
        from app.services.image_to_pdf_service import images_to_pdf_service
        from starlette.concurrency import run_in_threadpool
        
        result_io = await run_in_threadpool(
            images_to_pdf_service,
            image_bytes_list
        )

        download_name = _get_filename(request.query_params.get("filename"), "converted.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Images-to-PDF failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")


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

        pdf_bytes = await _read_upload_in_memory(files[0])
        result_io = add_page_numbers_in_memory(
            pdf_bytes=pdf_bytes,
            position=position,
            format_str=fmt_str,
            start_num=start_n,
            margin=margin,
            font_size=font_size
        )

        download_name = _get_filename(request.query_params.get("filename"), "numbered.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Add Page Numbers failed")
        raise HTTPException(status_code=500, detail=f"Adding page numbers failed: {exc}")

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

    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        result_io = crop_pdf_in_memory(
            pdf_bytes,
            top_m,
            bottom_m,
            left_m,
            right_m,
            unit,
            apply_to,
            range
        )

        download_name = _get_filename(request.query_params.get("filename"), "cropped.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Crop PDF failed")
        raise HTTPException(status_code=500, detail=f"Cropping PDF failed: {exc}")

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

    try:
        order_array = json.loads(page_order)
        if not isinstance(order_array, list):
            raise ValueError("page_order must be a JSON array")
        
        pdf_bytes = await _read_upload_in_memory(file)
        result_io = organize_pdf_in_memory(pdf_bytes, order_array)

        download_name = _get_filename(request.query_params.get("filename"), "organized.pdf")

        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for page_order")
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Organize PDF failed")
        raise HTTPException(status_code=500, detail=f"Organizing PDF failed: {exc}")

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
    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        from starlette.concurrency import run_in_threadpool
        
        result_io = await run_in_threadpool(
            pdf_to_word_in_memory,
            pdf_bytes,
            str(UPLOAD_DIR),
            str(OUTPUT_DIR)
        )
        
        download_name = _get_filename(request.query_params.get("filename"), "converted.docx")
        
        return StreamingResponse(
            result_io,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("PDF-to-Word failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

@router.post("/tools/pdf-to-excel", summary="Convert a PDF to an Excel spreadsheet")
@limiter.limit("10/minute")
async def pdf_to_excel_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PDF file is required.")

    validate_pdf_uploads([files[0]])
    try:
        import time
        start_time = time.time()
        
        pdf_bytes = await _read_upload_in_memory(files[0])
        read_time = time.time() - start_time
        logger.info(f"File read time: {read_time:.3f}s")
        
        from starlette.concurrency import run_in_threadpool
        
        gen_start_time = time.time()
        result_io = await run_in_threadpool(
            pdf_to_excel_in_memory,
            pdf_bytes,
        )
        gen_time = time.time() - gen_start_time
        logger.info(f"Excel generation time: {gen_time:.3f}s")
        
        download_name = _get_filename(request.query_params.get("filename"), "converted.xlsx")
        
        return StreamingResponse(
            result_io,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("PDF-to-Excel failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

@router.post("/tools/excel-to-pdf", summary="Convert an Excel file to a PDF document")
@limiter.limit("10/minute")
async def excel_to_pdf_endpoint(
    request: Request,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="An Excel file is required.")

    validate_excel_uploads([files[0]])
    try:
        import time
        start_time = time.time()
        
        file_bytes = await _read_upload_in_memory(files[0])
        read_time = time.time() - start_time
        logger.info(f"Excel to PDF: File read time: {read_time:.3f}s")
        
        from starlette.concurrency import run_in_threadpool
        
        result_io = await run_in_threadpool(
            excel_to_pdf_service,
            file_bytes,
        )
        
        download_name = _get_filename(request.query_params.get("filename"), "converted.pdf")
        
        return StreamingResponse(
            result_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Excel-to-PDF failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

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
    try:
        pdf_bytes = await _read_upload_in_memory(files[0])
        
        from starlette.concurrency import run_in_threadpool
        
        result_io, media_type, ext = await run_in_threadpool(
            pdf_to_jpg_in_memory,
            pdf_bytes,
            quality
        )
        
        filename = f"converted{ext}"
        download_name = _get_filename(request.query_params.get("filename"), filename)
        
        return StreamingResponse(
            result_io,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("PDF-to-JPG failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

@router.post("/tools/word-to-pdf", summary="Convert a DOCX or DOC file into a PDF document")
@limiter.limit("10/minute")
async def word_to_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A Word document is required.")

    validate_docx_uploads([files[0]])
    try:
        import time
        t_start = time.time()
        
        file_bytes = await _read_upload_in_memory(files[0])
        upload_time = time.time() - t_start
        logger.info(f"Word to PDF: File upload to backend processed in {upload_time:.3f}s")
        
        from starlette.concurrency import run_in_threadpool
        
        pdf_path, temp_files, timings = await run_in_threadpool(
            word_to_pdf_service,
            file_bytes,
            files[0].filename
        )
        
        # We can read the PDF file into a memory buffer to stream it. 
        # This safely detaches it from the disk allowing _cleanup to wipe the file immediately after sending.
        import io
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        # Enqueue cleanup task directly to FastAPI's cleanup pipeline matching our temp files array.
        background_tasks.add_task(_cleanup, *temp_files)
        
        t_stream_start = time.time()
        
        download_name = _get_filename(request.query_params.get("filename"), "converted.pdf")
        
        response = StreamingResponse(
            pdf_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
        stream_time = time.time() - t_stream_start
        logger.info(f"Word to PDF: Stream prep time {stream_time:.3f}s")
        
        return response

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Word-to-PDF failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")

@router.post("/tools/ppt-to-pdf", summary="Convert a PPTX or PPT file into a PDF document")
@limiter.limit("10/minute")
async def ppt_to_pdf_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="A PowerPoint document is required.")

    validate_ppt_uploads([files[0]])
    try:
        import time
        t_start = time.time()
        
        file_bytes = await _read_upload_in_memory(files[0])
        upload_time = time.time() - t_start
        logger.info(f"PowerPoint to PDF: File upload to backend processed in {upload_time:.3f}s")
        
        from starlette.concurrency import run_in_threadpool
        
        pdf_path, temp_files, timings = await run_in_threadpool(
            ppt_to_pdf_service,
            file_bytes,
            files[0].filename
        )
        
        import io
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        background_tasks.add_task(_cleanup, *temp_files)
        
        t_stream_start = time.time()
        
        download_name = _get_filename(request.query_params.get("filename"), "converted.pdf")
        
        response = StreamingResponse(
            pdf_io,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
        )
        stream_time = time.time() - t_stream_start
        logger.info(f"PowerPoint to PDF: Stream prep time {stream_time:.3f}s")
        
        return response

    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("PowerPoint-to-PDF failed")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}")
