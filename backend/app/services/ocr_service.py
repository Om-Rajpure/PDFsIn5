"""
ocr_service.py
-------------------
Extracts selectable text layers from scanned images via Tesseract OCR mapped natively into PyMuPDF.
"""

import io
import os
import shutil
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

def ocr_pdf_service(file_bytes: bytes) -> tuple[io.BytesIO, str]:
    """
    Renders PDF pages directly into high DPI images and utilizes Tesseract OCR creating a synthesized searchable PDF construct.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
            
    Returns:
        A tuple of (io.BytesIO consisting of OCR'd PDF, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    engine_path = shutil.which("tesseract")
    if not engine_path:
        logger.error("Tesseract Engine not found within system PATH bindings.")
        raise ValueError("System OCR engine (Tesseract) is currently not installed. Cannot proceed with conversion.")
        
    start_time = time.time()
    logger.info(f"Starting PDF OCR Engine mapping. Size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    output_file_path = os.path.join(temp_dir, "ocr.pdf")
    
    try:
        t_save_start = time.time()
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File save time: {time.time() - t_save_start:.3f}s")
        
        # 1. Native rendering to Image & OCR Extraction Pipeline
        t_ocr_start = time.time()
        try:
            import fitz
            from PIL import Image
            import pytesseract
            
            # Map system paths explicitly for Windows configurations just in case (safe fail bindings)
            if os.name == 'nt' and engine_path:
                pytesseract.pytesseract.tesseract_cmd = engine_path

            # Create an empty shell collection holding new PDF planes
            output_pdf = fitz.open()

            with fitz.open(input_file_path) as target_pdf:
                total_pages = len(target_pdf)
                for page_num, page in enumerate(target_pdf):
                    logger.debug(f"Processing OCR mapping iteration on Page {page_num + 1} of {total_pages}")
                    t_page_start = time.time()
                    
                    # 1a. Native PyMuPDF Rendering Array (high resolution caching)
                    pix = page.get_pixmap(dpi=300)
                    # Force byte array directly to RGB parsing preventing alpha channel masking crashes
                    if pix.alpha:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    
                    # 1b. Byte array conversion leveraging PIL
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    logger.debug(f"Page {page_num + 1} rendering mapped in: {time.time() - t_page_start:.3f}s")
                    
                    # 1c. Heavy Threading execution triggering Tesseract subprocesses
                    t_tesseract_start = time.time()
                    try:
                        pdf_bytes_hocr = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    except Exception as t_err:
                        logger.error(f"Tesseract binary crashed mapping image to PDF: {t_err}")
                        raise ValueError(f"OCR engine failed extracting text structure on page {page_num + 1}.")
                    logger.debug(f"Page {page_num + 1} OCR processing executed in: {time.time() - t_tesseract_start:.3f}s")
                    
                    # 1d. Synthesis Layer merging OCR raw byte structures into target cache PDF
                    ocr_doc = fitz.open("pdf", pdf_bytes_hocr)
                    output_pdf.insert_pdf(ocr_doc)
                    ocr_doc.close()

            # Optimize cache utilizing complete deflation destroying raw garbage paths
            t_merge_start = time.time()
            output_pdf.save(output_file_path, garbage=3, deflate=True)
            output_pdf.close()
            logger.info(f"OCR layer combining and cache purge executed in: {time.time() - t_merge_start:.3f}s")
                
            logger.info(f"Complete OCR Document pipeline runtime: {time.time() - t_ocr_start:.3f}s")
            
        except ImportError as ie:
            logger.error(f"Critical module unmapped preventing OCR execution: {ie}")
            raise ValueError("The server backend environment is missing required internal OCR libraries integrations.")
        except Exception as e:
            logger.exception(f"Unexpected systemic crash scanning/mapping document OCR layers: {str(e)}")
            raise ValueError(f"Core execution failed attempting to parse OCR mapping: {str(e)}")
            
        # 2. Validation and return streaming logic
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            raise ValueError("OCR pipeline aborted resulting in an empty or missing output configuration.")
            
        with open(output_file_path, "rb") as f:
            final_ocr_bytes = f.read()
            
        buffer = io.BytesIO(final_ocr_bytes)
        buffer.seek(0)
        
        total_time = time.time() - start_time
        logger.info(f"Total OCR API handling completed within {total_time:.3f}s.")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        logger.exception(f"Unknown runtime error triggered rendering OCR cache drops: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error occurred resolving the OCR document requests. Please ensure it is a valid scanned PDF image structure and try again.")
