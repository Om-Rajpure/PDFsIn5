import io
import base64
import logging
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

def get_pdf_previews_in_memory(pdf_bytes: bytes) -> dict:
    """
    Reads the PDF and returns page count and a list of base64 JPEG previews.
    
    Args:
        pdf_bytes: Raw PDF bytes.
        
    Returns:
        A dict: {"page_count": int, "previews": list[str]}
    """
    try:
        doc = fitz.open("pdf", pdf_bytes)
        page_count = len(doc)
        previews = []
        
        # We use a low zoom factor for small and fast thumbnails
        matrix = fitz.Matrix(0.5, 0.5)
        
        for i in range(page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            img_bytes = pix.tobytes("jpeg")
            b64_str = base64.b64encode(img_bytes).decode("ascii")
            previews.append(f"data:image/jpeg;base64,{b64_str}")
            
        doc.close()
        return {
            "page_count": page_count,
            "previews": previews
        }
    except Exception as exc:
        raise RuntimeError(f"Failed to generate previews: {exc}") from exc

def organize_pdf_in_memory(pdf_bytes: bytes, page_order: list[int]) -> io.BytesIO:
    """
    Creates a new PDF by arranging pages from the original PDF according to `page_order`.
    Uses pypdf as per requirements.
    
    Args:
        pdf_bytes: Raw PDF bytes.
        page_order: List of 1-indexed page numbers in the desired sequence.
        
    Returns:
        io.BytesIO containing the new PDF data.
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        
        # Note: page_order is 1-indexed array of page numbers e.g., [3, 1, 2]
        # pypdf pages are 0-indexed.
        total_pages = len(reader.pages)
        
        for pnum in page_order:
            if 1 <= pnum <= total_pages:
                writer.add_page(reader.pages[pnum - 1])
                
        out_io = io.BytesIO()
        writer.write(out_io)
        out_io.seek(0)
        
        return out_io
    except Exception as exc:
        raise RuntimeError(f"Failed to organize PDF: {exc}") from exc
