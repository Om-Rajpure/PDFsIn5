"""
image_to_pdf_service.py
-----------------------
Converts images to PDF entirely in-memory using parallel processing (ThreadPoolExecutor).
Strategy:
  1. ThreadPoolExecutor normalises images to RGB JPEG bytes concurrently.
  2. Feed resulting bytes to img2pdf for layout conversion directly in memory.
"""

import io
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import img2pdf

logger = logging.getLogger(__name__)

MAX_DIM = 4000

def _normalise_image_bytes(img_bytes: bytes, orientation: str) -> bytes:
    """
    Open an image from bytes, convert to RGB, optionally down-scale,
    handle orientation rotation if landscape, and return JPEG bytes.
    """
    with Image.open(io.BytesIO(img_bytes)) as img:
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        w, h = img.size
        # Downscale if > max dim
        if w > MAX_DIM or h > MAX_DIM:
            ratio = min(MAX_DIM / w, MAX_DIM / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            w, h = img.size

        # If Landscape requested and image is portrait, rotate it
        if orientation.lower() == "landscape" and w < h:
            img = img.rotate(90, expand=True)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue()

def images_to_pdf_in_memory(image_bytes_list: list[bytes], orientation: str = "Portrait") -> io.BytesIO:
    """
    Convert a list of image bytes into a combined PDF in-memory using parallel processing.

    Args:
        image_bytes_list: Ordered list of raw image bytes.
        orientation: 'Portrait' or 'Landscape'.

    Returns:
        io.BytesIO containing the generated PDF data.
    """
    if not image_bytes_list:
        raise ValueError("At least one image is required.")

    # Process images concurrently
    jpeg_buffers = [None] * len(image_bytes_list)
    
    with ThreadPoolExecutor() as executor:
        # submit tasks remembering their original index structure
        future_to_index = {
            executor.submit(_normalise_image_bytes, img_bytes, orientation): i
            for i, img_bytes in enumerate(image_bytes_list)
        }
        
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                jpeg_buffers[i] = future.result()
            except Exception as exc:
                raise RuntimeError(f"Failed to process image at index {i}: {exc}") from exc

    # assemble with img2pdf
    try:
        pdf_bytes = img2pdf.convert(jpeg_buffers)
        out_io = io.BytesIO(pdf_bytes)
        out_io.seek(0)
    except Exception as exc:
        raise RuntimeError(f"img2pdf conversion failed: {exc}") from exc

    logger.info("Images-to-PDF generated in-memory (%d pages)", len(image_bytes_list))
    return out_io
