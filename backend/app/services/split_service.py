"""
split_service.py
----------------
Splits a PDF file in-memory using PyMuPDF (fitz) for maximum performance.
Supports extracting every page into separate PDFs or extracting specific page ranges.
Returns a ZIP archive if multiple files are generated, or a single PDF if only one is generated.
"""

import io
import fitz  # PyMuPDF
import logging
import zipfile

logger = logging.getLogger(__name__)

def parse_ranges(ranges_str: str, max_pages: int) -> list[tuple[int, int]]:
    """
    Parses a string like "1-3, 5, 7-9" into a list of 0-based index tuples containing (start, end).
    Note: end index is inclusive for PyMuPDF extraction logic.
    """
    ranges = []
    if not ranges_str:
        return ranges
        
    parts = [p.strip() for p in ranges_str.split(',')]
    for part in parts:
        if not part:
            continue
        if '-' in part:
            subparts = part.split('-')
            if len(subparts) == 2:
                try:
                    start = max(1, int(subparts[0].strip()))
                    end = min(max_pages, int(subparts[1].strip()))
                    if start <= end:
                        ranges.append((start - 1, end - 1))
                except ValueError:
                    pass
        else:
            try:
                page = int(part)
                if 1 <= page <= max_pages:
                    ranges.append((page - 1, page - 1))
            except ValueError:
                pass
                
    return ranges

def split_pdf_in_memory(pdf_bytes: bytes, mode: str, ranges_str: str) -> tuple[io.BytesIO, str, str]:
    """
    Splits a PDF in-memory.
    
    Args:
        pdf_bytes: Raw PDF bytes.
        mode: "Extract range" or "Split every page"
        ranges_str: Comma separated ranges like "1-3, 5-7"
        
    Returns:
        tuple containing:
        - io.BytesIO stream of the result (PDF or ZIP)
        - media_type (e.g. "application/pdf" or "application/zip")
        - filename (e.g. "split-result.pdf" or "split-results.zip")
    """
    try:
        doc = fitz.open("stream", pdf_bytes, "pdf")
    except Exception as exc:
        raise ValueError(f"Invalid PDF file: {exc}")

    max_pages = doc.page_count
    generated_pdfs = [] # list of tuples (filename, bytes)

    if mode == "Extract range":
        ranges = parse_ranges(ranges_str, max_pages)
        if not ranges:
            doc.close()
            raise ValueError("Invalid or missing page ranges. Use format like '1-3, 5'.")
            
        for idx, (start, end) in enumerate(ranges):
            new_doc = fitz.open()
            # PyMuPDF insert_pdf takes from_page and to_page (inclusive)
            new_doc.insert_pdf(doc, from_page=start, to_page=end)
            pdf_data = new_doc.write()
            new_doc.close()
            generated_pdfs.append((f"split_range_{start+1}_to_{end+1}.pdf", pdf_data))
            
    else: # "Split every page" (or default fallback)
        for i in range(max_pages):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            pdf_data = new_doc.write()
            new_doc.close()
            generated_pdfs.append((f"page_{i+1}.pdf", pdf_data))
            
    doc.close()

    if not generated_pdfs:
        raise ValueError("Could not split PDF. No valid pages matched criteria.")

    # Return a single PDF
    if len(generated_pdfs) == 1:
        out_io = io.BytesIO(generated_pdfs[0][1])
        out_io.seek(0)
        return out_io, "application/pdf", generated_pdfs[0][0]

    # Return a ZIP file containing multiple PDFs
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for filename, pdf_data in generated_pdfs:
            zipf.writestr(filename, pdf_data)
            
    zip_io.seek(0)
    return zip_io, "application/zip", "split-results.zip"
