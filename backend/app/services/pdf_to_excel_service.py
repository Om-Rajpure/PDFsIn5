import io
import fitz  # PyMuPDF
import pandas as pd
import tempfile
import aiofiles
import os
import logging
from typing import List, Tuple

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

logger = logging.getLogger(__name__)

def pdf_to_excel_in_memory(pdf_bytes: bytes) -> io.BytesIO:
    """
    Convert a PDF file to an Excel file using camelot for tables and
    falling back to PyMuPDF for text abstraction if no tables are found.
    Returns a BytesIO object containing the Excel file.
    """
    output_buffer = io.BytesIO()
    
    # We must write bytes to a temp file because Camelot requires a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_bytes)
        tmp_pdf_path = tmp_pdf.name

    tables_extracted = False
    
    try:
        # 1. Attempt Camelot Extraction
        if CAMELOT_AVAILABLE:
            try:
                logger.info("Attempting table extraction with camelot...")
                tables = camelot.read_pdf(tmp_pdf_path, pages='all', flavor='lattice')
                if not tables:
                    tables = camelot.read_pdf(tmp_pdf_path, pages='all', flavor='stream')
                
                if tables and len(tables) > 0:
                    tables_extracted = True
                    logger.info(f"Found {len(tables)} tables using camelot.")
                    
                    with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                        for idx, table in enumerate(tables):
                            df = table.df
                            sheet_name = f"Table {idx + 1}"
                            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
            except Exception as e:
                logger.warning(f"Camelot extraction failed or encountered an error: {e}")
        
        # 2. Fallback to PyMuPDF Text Extraction if no tables were found
        if not tables_extracted:
            logger.info("Falling back to PyMuPDF text extraction...")
            doc = fitz.open("pdf", pdf_bytes)
            
            with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text("text")
                    
                    if not text.strip():
                        # Handle empty pages
                        df = pd.DataFrame([["(Empty Page)"]])
                    else:
                        rows = text.split('\n')
                        # We just put each line in a new row in the first column
                        df = pd.DataFrame(rows, columns=["Extracted Text"])
                    
                    sheet_name = f"Page {page_num + 1}"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            doc.close()

    finally:
        # Ensure temporary file is always deleted
        if os.path.exists(tmp_pdf_path):
            try:
                os.remove(tmp_pdf_path)
            except Exception as e:
                logger.error(f"Failed to delete temporary file {tmp_pdf_path}: {e}")

    output_buffer.seek(0)
    return output_buffer
