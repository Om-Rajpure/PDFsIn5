import io
import time
import logging
import img2pdf

logger = logging.getLogger(__name__)

def images_to_pdf_service(files_bytes_list: list[bytes]) -> io.BytesIO:
    """
    Converts a list of image byte streams directly into a single PDF in memory.
    """
    if not files_bytes_list:
        raise ValueError("No images provided for conversion.")

    t0 = time.time()
    
    try:
        # Convert the list of raw image bytes directly to PDF bytes
        # img2pdf handles PNG/JPG seamlessly without re-encoding
        pdf_bytes = img2pdf.convert(files_bytes_list)
        gen_time = time.time() - t0
        logger.info(f"Images to PDF: PDF generated in {gen_time:.3f}s for {len(files_bytes_list)} images.")
        
        # Write to BytesIO and seek 0 for streaming response compatibility
        pdf_io = io.BytesIO(pdf_bytes)
        pdf_io.seek(0)
        
        return pdf_io
        
    except img2pdf.ImageOpenError as e:
        logger.error(f"Images to PDF failed due to invalid image bytes: {e}")
        raise ValueError(f"One or more images could not be parsed: {e}")
    except Exception as e:
        logger.exception("Images to PDF: Critical conversion error.")
        raise RuntimeError(f"Failed to generate PDF from images: {e}")
