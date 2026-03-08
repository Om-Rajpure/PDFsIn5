"""
redact_service.py
-------------------
Permanently redacts specific text strings from a PDF utilizing PyMuPDF (fitz).
"""

import io
import os
import shutil
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

def redact_pdf_service(file_bytes: bytes, redact_text: str) -> tuple[io.BytesIO, str]:
    """
    Search and permanently censor a target text string across all pages in a PDF document.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
        redact_text: Exact string to locate and apply black redaction boxes to.
            
    Returns:
        A tuple of (io.BytesIO consisting of redacted PDF, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    if not redact_text or not redact_text.strip():
        raise ValueError("Redaction text cannot be empty.")
        
    start_time = time.time()
    logger.info(f"Starting PDF Redaction logic. Target string: '{redact_text}' Size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    output_file_path = os.path.join(temp_dir, "redacted.pdf")
    
    try:
        t_save_start = time.time()
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File save time: {time.time() - t_save_start:.3f}s")
        
        # 1. Open natively utilizing PyMuPDF
        t_redact_start = time.time()
        matches_found = 0
        try:
            import fitz
            
            with fitz.open(input_file_path) as doc:
                for page in doc:
                    # Leverage robust text search matrix extracting bounding boxes mapping directly to target
                    rects = page.search_for(redact_text)
                    
                    if rects:
                        for rect in rects:
                            # Apply native explicit blackout fill boundaries locking graphical layers natively
                            page.add_redact_annot(rect, fill=(0, 0, 0))
                            matches_found += 1
                        
                        # Purge physical traces destroying graphical intersections mapped per page dynamically
                        page.apply_redactions()
                
                # Overwrite cache with hard garbage dropping configurations mapped to save optimization
                doc.save(output_file_path, garbage=3, deflate=True)
                
            logger.info(f"PDF content redaction execution time: {time.time() - t_redact_start:.3f}s. Redacted {matches_found} occurrences.")
            
        except ImportError:
            logger.error("pymupdf library (fitz) is not installed properly.")
            raise ValueError("Redaction engine relies on internal dependencies currently unavailable.")
        except Exception as e:
            logger.exception(f"Exception while scanning/redacting document layers: {str(e)}")
            raise ValueError(f"Core execution failed processing text redactions: {str(e)}")
            
        # 2. Validation and BytesIO Output Stream
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            raise ValueError("Redaction engine failed rendering correct file configurations.")
            
        with open(output_file_path, "rb") as f:
            redacted_bytes = f.read()
            
        buffer = io.BytesIO(redacted_bytes)
        buffer.seek(0)
        
        total_time = time.time() - start_time
        logger.info(f"Total redacting pipeline completed in {total_time:.3f}s.")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        logger.exception(f"Unexpected native error executing redact isolation: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error blocked execution attempting to redact the document.")
