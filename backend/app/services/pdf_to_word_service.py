"""
pdf_to_word_service.py
----------------------
Converts a PDF file to a Microsoft Word (.docx) document using pdf2docx.

pdf2docx performs layout analysis and attempts to reconstruct paragraphs,
tables, and images as closely as possible to the original PDF rendering.
"""

import os
import uuid
import logging
from pdf2docx import Converter

logger = logging.getLogger(__name__)


def pdf_to_word(input_path: str, output_dir: str) -> str:
    """
    Convert a PDF file to a DOCX document.

    Args:
        input_path: Absolute path to the source PDF.
        output_dir: Directory where the DOCX will be saved.

    Returns:
        Absolute path to the generated .docx file.

    Raises:
        FileNotFoundError: If the source PDF does not exist.
        RuntimeError: On any conversion failure.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"converted_{uuid.uuid4().hex}.docx"
    output_path = os.path.join(output_dir, output_filename)

    cv = None
    try:
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        logger.info("PDF converted to Word: %s → %s", input_path, output_path)
    except Exception as exc:
        raise RuntimeError(f"pdf2docx conversion failed: {exc}") from exc
    finally:
        if cv is not None:
            try:
                cv.close()
            except Exception:
                pass

    if not os.path.isfile(output_path):
        raise RuntimeError("DOCX output file was not created.")

    return output_path
