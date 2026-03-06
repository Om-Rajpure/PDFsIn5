"""
merge_service.py
----------------
Merges multiple PDF files in-memory using PyMuPDF (fitz) for maximum performance.
"""

import io
import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

def merge_pdfs_in_memory(pdf_bytes_list: list[bytes]) -> io.BytesIO:
    """
    Merge a list of PDF bytes into a single PDF in-memory.

    Args:
        pdf_bytes_list: Ordered list of raw PDF bytes.

    Returns:
        io.BytesIO containing the merged PDF data.

    Raises:
        ValueError: If fewer than 2 input files are provided.
        RuntimeError: If document merging fails.
    """
    if len(pdf_bytes_list) < 1:
        raise ValueError("At least one PDF file is required to merge.")

    merged_doc = fitz.open()

    for i, pdf_bytes in enumerate(pdf_bytes_list):
        try:
            doc = fitz.open("pdf", pdf_bytes)
            merged_doc.insert_pdf(doc)
            doc.close()
        except Exception as exc:
            merged_doc.close()
            raise RuntimeError(f"Failed to read PDF at index {i}: {exc}") from exc

    output_bytes = merged_doc.write()
    merged_doc.close()

    logger.info("Merged %d PDFs in-memory", len(pdf_bytes_list))
    
    out_io = io.BytesIO(output_bytes)
    out_io.seek(0)
    return out_io
