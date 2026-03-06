"""
merge_service.py
----------------
Merges multiple uploaded PDF files into a single PDF using PyPDF2.
"""

import os
import uuid
import logging
from pypdf import PdfWriter, PdfReader

logger = logging.getLogger(__name__)


def merge_pdfs(input_paths: list[str], output_dir: str) -> str:
    """
    Merge a list of PDF file paths into a single PDF.

    Args:
        input_paths: Ordered list of absolute paths to the source PDFs.
        output_dir:  Directory where the merged PDF will be saved.

    Returns:
        Absolute path to the merged output PDF.

    Raises:
        ValueError: If fewer than 2 input files are provided.
        FileNotFoundError: If any input path does not exist.
    """
    if len(input_paths) < 1:
        raise ValueError("At least one PDF file is required to merge.")

    for path in input_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Input file not found: {path}")

    writer = PdfWriter()

    for path in input_paths:
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
            logger.info("Added %d pages from %s", len(reader.pages), path)
        except Exception as exc:
            raise RuntimeError(f"Failed to read PDF '{path}': {exc}") from exc

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"merged_{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    logger.info("Merged PDF saved to %s", output_path)
    return output_path
