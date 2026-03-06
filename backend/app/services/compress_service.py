"""
compress_service.py
-------------------
Compresses a PDF in-memory using pikepdf.
"""

import io
import logging
import pikepdf

logger = logging.getLogger(__name__)

QUALITY_PROFILES = {
    "Extreme compression (smallest)": {
        "compress_streams": True,
        "object_stream_mode": pikepdf.ObjectStreamMode.generate,
        "stream_decode_level": pikepdf.StreamDecodeLevel.generalized,
        "recompress_flate": True,
        "normalize_content": True,
    },
    "Recommended": {
        "compress_streams": True,
        "object_stream_mode": pikepdf.ObjectStreamMode.generate,
        "stream_decode_level": pikepdf.StreamDecodeLevel.none,
        "recompress_flate": False,
        "normalize_content": False,
    },
    "Less compression (best quality)": {
        "compress_streams": False,
        "object_stream_mode": pikepdf.ObjectStreamMode.preserve,
        "stream_decode_level": pikepdf.StreamDecodeLevel.none,
        "recompress_flate": False,
        "normalize_content": False,
    },
}

DEFAULT_QUALITY = "Recommended"

def compress_pdf_in_memory(pdf_bytes: bytes, quality: str = DEFAULT_QUALITY) -> io.BytesIO:
    """
    Compress PDF bytes in-memory using pikepdf.

    Args:
        pdf_bytes: Raw bytes of the input PDF.
        quality: One of the QUALITY_PROFILES keys.

    Returns:
        io.BytesIO containing the compressed PDF data.
    """
    profile = QUALITY_PROFILES.get(quality, QUALITY_PROFILES[DEFAULT_QUALITY])
    
    in_io = io.BytesIO(pdf_bytes)
    out_io = io.BytesIO()

    try:
        with pikepdf.open(in_io) as pdf:
            pdf.save(
                out_io,
                compress_streams=profile["compress_streams"],
                object_stream_mode=profile["object_stream_mode"],
                stream_decode_level=profile["stream_decode_level"],
                recompress_flate=profile["recompress_flate"],
                normalize_content=profile["normalize_content"],
            )
    except Exception as exc:
        raise RuntimeError(f"Failed to compress PDF: {exc}") from exc

    reduction = (1 - out_io.getbuffer().nbytes / len(pdf_bytes)) * 100 if len(pdf_bytes) else 0

    logger.info("Compressed PDF in-memory: %.1f%% reduction", reduction)
    
    out_io.seek(0)
    return out_io
