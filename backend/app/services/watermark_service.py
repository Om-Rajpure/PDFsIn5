"""
watermark_service.py
-------------------
Watermarks a PDF using reportlab for generation and pikepdf for merging.
"""

import io
import os
import shutil
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

def watermark_pdf_service(file_bytes: bytes, watermark_text: str, **kwargs) -> tuple[io.BytesIO, str]:
    """
    Applies a text watermark to every page in a PDF document.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
        watermark_text: String to draw across pages.
        **kwargs: Extensible configurations (opacity, position, etc.) for future enhancements.
            
    Returns:
        A tuple of (io.BytesIO consisting of watermarked PDF, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    if not watermark_text or not watermark_text.strip():
        raise ValueError("Watermark text cannot be empty.")
    watermark_text = watermark_text.strip()
        
    start_time = time.time()
    logger.info(f"Starting PDF Watermarking. Size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    watermark_file_path = os.path.join(temp_dir, "watermark.pdf")
    output_file_path = os.path.join(temp_dir, "watermarked.pdf")
    
    try:
        t_save_start = time.time()
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File save time: {time.time() - t_save_start:.3f}s")
        
        # 1. Generate the watermark layer mapping using reportlab
        t_gen_start = time.time()
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Using letter size as an arbitrary large wrapper plane (it will get natively scaled/overlayed accurately)
            width, height = letter
            c = canvas.Canvas(watermark_file_path, pagesize=letter)
            
            # Future expansion parameter parsing 
            opacity = kwargs.get('opacity', 0.5)
            font_size = kwargs.get('font_size', 70)
            
            c.setFont("Helvetica", font_size)
            
            # Center the watermark matrix
            c.translate(width / 2.0, height / 2.0)
            
            # Set opacity (Fill Alpha) & Grey color binding
            c.setFillAlpha(opacity)
            c.setFillGray(0.5) 
            
            # Rotate Canvas
            c.rotate(45)
            
            # Draw exact centered text relative to new rotated anchor
            c.drawCentredString(0, 0, watermark_text)
            c.save()
            
            logger.info(f"Watermark layer generation time: {time.time() - t_gen_start:.3f}s")
            
        except Exception as e:
            logger.exception(f"Exception while generating watermark PDF layer: {str(e)}")
            raise ValueError(f"Failed to generate watermark overlay: {str(e)}")
            
        # 2. Merge via PikePDF Overlays
        t_merge_start = time.time()
        try:
            import pikepdf
            
            with pikepdf.Pdf.open(input_file_path) as target_pdf:
                with pikepdf.Pdf.open(watermark_file_path) as watermark_pdf:
                    watermark_page = watermark_pdf.pages[0]
                    
                    for page in target_pdf.pages:
                        page = pikepdf.Page(page)
                        page.add_overlay(watermark_page)
                    
                    target_pdf.save(output_file_path)
                    
            logger.info(f"PDF page merging time: {time.time() - t_merge_start:.3f}s")
            
        except Exception as e:
            logger.exception(f"Exception while merging watermark PDF planes: {str(e)}")
            raise ValueError(f"Merging failed. The file may be heavily corrupted or read-only: {str(e)}")
            
        # 3. Validation and BytesIO Output
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            raise ValueError("Watermark engine did not produce output file or file is empty.")
            
        with open(output_file_path, "rb") as f:
            watermarked_bytes = f.read()
            
        buffer = io.BytesIO(watermarked_bytes)
        buffer.seek(0)
        
        total_time = time.time() - start_time
        logger.info(f"Total watermarking process completed in {total_time:.3f}s.")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        logger.exception(f"Unexpected error during PDF watermarking: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error occurred during watermarking. Please try again.")
