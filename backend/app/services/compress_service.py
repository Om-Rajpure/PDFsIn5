"""
compress_service.py
-------------------
Compresses a PDF using pikepdf, which re-writes the internal structure
and removes dead objects, cross-reference streams, and unused data.

Quality levels:
    extreme   → aggressive object compression + no metadata
    medium    → balanced (default)
    light     → minimal compression, preserves quality
"""

import os
import uuid
import logging
import pikepdf

logger = logging.getLogger(__name__)

# Maps user-facing quality labels to pikepdf compression settings
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


def compress_pdf(input_path: str, output_dir: str, quality: str = DEFAULT_QUALITY) -> str:
    """
    Compress a PDF file using pikepdf.

    Args:
        input_path: Absolute path to the source PDF.
        output_dir: Directory where the compressed PDF will be saved.
        quality:    One of the QUALITY_PROFILES keys.

    Returns:
        Absolute path to the compressed output PDF.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    profile = QUALITY_PROFILES.get(quality, QUALITY_PROFILES[DEFAULT_QUALITY])

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"compressed_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(
                output_path,
                compress_streams=profile["compress_streams"],
                object_stream_mode=profile["object_stream_mode"],
                stream_decode_level=profile["stream_decode_level"],
                recompress_flate=profile["recompress_flate"],
                normalize_content=profile["normalize_content"],
            )
    except Exception as exc:
        raise RuntimeError(f"Failed to compress PDF: {exc}") from exc

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    reduction = (1 - compressed_size / original_size) * 100 if original_size else 0

    logger.info(
        "Compressed PDF: %s → %s (%.1f%% reduction)",
        input_path, output_path, reduction,
    )
    return output_path
