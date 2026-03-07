"""
rotate_service.py
-----------------
Rotates pages in a PDF file in-memory using PyMuPDF (fitz) for maximum performance.
Supports rotating all pages or specific page ranges by 90, 180, or 270 degrees.
"""

import io
import fitz  # PyMuPDF
import logging
from app.services.split_service import parse_ranges

logger = logging.getLogger(__name__)

def rotate_pdf_in_memory(pdf_bytes: bytes, angle_str: str, apply_to: str, range_str: str) -> io.BytesIO:
    """
    Rotates a PDF in-memory.
    
    Args:
        pdf_bytes: Raw PDF bytes.
        angle_str: "Rotate 90° clockwise", "Rotate 180°", "Rotate 270° clockwise", etc.
        apply_to: "All pages" or "Specific page range"
        range_str: Comma separated ranges like "1-3, 5-7"
        
    Returns:
        io.BytesIO stream of the mutated PDF
    """
    try:
        doc = fitz.open("stream", pdf_bytes, "pdf")
    except Exception as exc:
        raise ValueError(f"Invalid PDF file: {exc}")

    # Parse angle
    angle = 0
    if "90" in angle_str:
        angle = 90
    elif "180" in angle_str:
        angle = 180
    elif "270" in angle_str:
        angle = 270

    pages_to_rotate = set()
    max_pages = doc.page_count

    if apply_to == "Specific page range":
        ranges = parse_ranges(range_str, max_pages)
        if not ranges:
            doc.close()
            raise ValueError("Invalid or missing page ranges. Use format like '1-3, 5'.")
            
        for start, end in ranges:
            for p in range(start, end + 1):
                pages_to_rotate.add(p)
    else:
        # "All pages" or fallback
        for p in range(max_pages):
            pages_to_rotate.add(p)

    if not pages_to_rotate:
        doc.close()
        raise ValueError("No valid pages selected for rotation.")

    # Apply rotation
    for i in range(max_pages):
        if i in pages_to_rotate:
            page = doc[i]
            # Add to any existing rotation
            new_rot = (page.rotation + angle) % 360
            page.set_rotation(new_rot)

    out_io = io.BytesIO()
    doc.save(out_io)
    doc.close()

    out_io.seek(0)
    return out_io
