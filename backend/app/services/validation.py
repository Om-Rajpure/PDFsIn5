"""
validation.py
-------------
FastAPI dependencies for shared request validation:
  - file size limit (50 MB per file)
  - allowed MIME types per tool category
"""

import logging
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

PDF_MIME_TYPES = {
    "application/pdf",
    "application/x-pdf",
}

IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/tiff",
}

DOCX_MIME_TYPES = {
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _check_size(upload: UploadFile) -> None:
    """Raise 413 if the file reports a size above the limit."""
    if upload.size is not None and upload.size > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File '{upload.filename}' is too large "
                f"({upload.size / (1024*1024):.1f} MB). "
                f"Maximum allowed size is {settings.MAX_FILE_SIZE_MB} MB."
            ),
        )


def _check_mime(upload: UploadFile, allowed: set[str], label: str) -> None:
    """Raise 415 if the content-type is not in the allowed set."""
    ct = (upload.content_type or "").split(";")[0].strip().lower()
    if ct and ct not in allowed:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type '{ct}' for file '{upload.filename}'. "
                f"Expected: {label}."
            ),
        )


# ── Public validators ────────────────────────────────────────────────────────

def validate_pdf_uploads(files: list[UploadFile]) -> list[UploadFile]:
    """Validate a list of PDF uploads for size and MIME type."""
    for f in files:
        _check_size(f)
        _check_mime(f, PDF_MIME_TYPES, "PDF")
    return files


def validate_image_uploads(files: list[UploadFile]) -> list[UploadFile]:
    """Validate a list of image uploads for size and MIME type."""
    for f in files:
        _check_size(f)
        _check_mime(f, IMAGE_MIME_TYPES, "JPG / PNG / WEBP")
    return files


def validate_single_upload(upload: UploadFile) -> UploadFile:
    """Generic single-file size check (no MIME restriction)."""
    _check_size(upload)
    return upload
