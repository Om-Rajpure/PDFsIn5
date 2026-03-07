import os
import io
import time
import uuid
import logging
import fitz
from pdf2docx import Converter
from docx import Document

logger = logging.getLogger(__name__)

def pdf_to_word_in_memory(
    pdf_bytes: bytes,
    upload_dir: str,
    output_dir: str
) -> io.BytesIO:
    """
    Hybrid PDF to Word Converter.
    - <= 10 pages: Uses pdf2docx temporarily writing to disk for perfect layout accuracy.
    - > 10 pages: Uses PyMuPDF + python-docx natively in RAM for instant processing.
    """
    start_time = time.time()
    
    # 1. Load length natively
    doc = fitz.open("pdf", pdf_bytes)
    page_count = len(doc)
    
    logger.info(f"PDF to Word initiated. Size: {page_count} pages. Loading took {time.time() - start_time:.2f}s")
    
    out_io = io.BytesIO()

    if page_count <= 10:
        # PATH A: High-accuracy layout conversion for small PDFs
        logger.info("Routing to High-Accuracy (pdf2docx) conversion.")
        
        # Write to temp files since pdf2docx requires filepaths
        in_filename = f"temp_in_{uuid.uuid4().hex}.pdf"
        out_filename = f"temp_out_{uuid.uuid4().hex}.docx"
        in_path = os.path.join(upload_dir, in_filename)
        out_path = os.path.join(output_dir, out_filename)
        
        with open(in_path, 'wb') as f:
            f.write(pdf_bytes)
            
        cv = None
        try:
            conv_start = time.time()
            cv = Converter(in_path)
            # Disable unnecessary layout configurations to maximize speed
            cv.convert(out_path, start=0, end=None, connected_border=False)
            logger.info(f"pdf2docx conversion finished natively in {time.time() - conv_start:.2f}s")
            
            with open(out_path, 'rb') as out_f:
                out_io.write(out_f.read())
        except Exception as exc:
            raise RuntimeError(f"pdf2docx conversion failed: {exc}") from exc
        finally:
            if cv is not None:
                try:
                    cv.close()
                except:
                    pass
            # Immediate cleanup
            if os.path.exists(in_path):
                os.remove(in_path)
            if os.path.exists(out_path):
                os.remove(out_path)
                
    else:
        # PATH B: Rapid Text Extraction for big PDFs
        logger.info("Routing to High-Speed Text Extraction (PyMuPDF) conversion.")
        conv_start = time.time()
        
        word_doc = Document()
        
        for i in range(page_count):
            page_text = doc[i].get_text("text")
            
            # Avoid empty pages creating blanks
            if page_text.strip():
                word_doc.add_paragraph(page_text)
            
            # add page break except on the last page
            if i < page_count - 1:
                word_doc.add_page_break()
                
        word_doc.save(out_io)
        logger.info(f"PyMuPDF + python-docx fast-extraction finished in {time.time() - conv_start:.2f}s")

    doc.close()
    out_io.seek(0)
    
    # Validation against empty or corrupted buffers
    if out_io.getbuffer().nbytes == 0:
        raise ValueError("PDF to Word conversion resulted in an empty file. Content may be fully flattened or protected.")
    
    logger.info(f"Total /pdf-to-word execution took {time.time() - start_time:.2f}s")
    return out_io
