"""
image_to_pdf_service.py
-----------------------
Converts one or more images (JPG, PNG, WEBP) into a single PDF.

Strategy:
  1. Use Pillow to normalise every image to RGB JPEG bytes.
  2. Feed the resulting byte buffers to img2pdf for a lossless-layout PDF.

This approach ensures consistent output regardless of input format.
"""

import io
import os
import uuid
import logging
from PIL import Image
import img2pdf

logger = logging.getLogger(__name__)

# Maximum dimension (pixels) for a single side; larger images are down-scaled.
MAX_DIM = 4000


def _normalise_image(path: str) -> bytes:
    """
    Open an image with Pillow, convert to RGB, optionally down-scale,
    and return JPEG bytes suitable for img2pdf.
    """
    with Image.open(path) as img:
        # Convert palette / RGBA / grayscale → RGB
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # Down-scale if image is unreasonably large
        w, h = img.size
        if w > MAX_DIM or h > MAX_DIM:
            ratio = min(MAX_DIM / w, MAX_DIM / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue()


def images_to_pdf(
    image_paths: list[str],
    output_dir: str,
    orientation: str = "Portrait",
) -> str:
    """
    Convert a list of image paths into a combined PDF.

    Args:
        image_paths: Ordered list of absolute paths to image files.
        output_dir:  Directory where the PDF will be saved.
        orientation: 'Portrait' or 'Landscape'.

    Returns:
        Absolute path to the generated PDF.
    """
    if not image_paths:
        raise ValueError("At least one image is required.")

    for path in image_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Image not found: {path}")

    # Normalise all images to JPEG bytes
    jpeg_buffers = []
    for path in image_paths:
        try:
            jpeg_buffers.append(_normalise_image(path))
            logger.info("Processed image: %s", path)
        except Exception as exc:
            raise RuntimeError(f"Failed to process image '{path}': {exc}") from exc

    # Set page size based on orientation
    if orientation.lower() == "landscape":
        layout = img2pdf.get_layout_fun(img2pdf.parse_pagesize_rectarg("A4"))
        # img2pdf doesn't have built-in landscape; rotate via Pillow instead
        rotated = []
        for buf in jpeg_buffers:
            with Image.open(io.BytesIO(buf)) as img:
                if img.width < img.height:          # portrait image on landscape page
                    img = img.rotate(90, expand=True)
                out = io.BytesIO()
                img.save(out, format="JPEG", quality=90)
                rotated.append(out.getvalue())
        jpeg_buffers = rotated

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"images_to_pdf_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    try:
        pdf_bytes = img2pdf.convert(jpeg_buffers)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception as exc:
        raise RuntimeError(f"img2pdf conversion failed: {exc}") from exc

    logger.info("Images-to-PDF saved to %s (%d pages)", output_path, len(image_paths))
    return output_path
