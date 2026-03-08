import io
import time
import zipfile
import fitz  # PyMuPDF
import logging
from typing import Tuple
from PIL import Image

logger = logging.getLogger(__name__)

def pdf_to_jpg_in_memory(pdf_bytes: bytes, quality: str = "Medium") -> Tuple[io.BytesIO, str, str]:
    """
    Convert a PDF into JPG images. 
    If 1 page, returns a JPG buffer. 
    If >1 pages, returns a ZIP buffer containing all JPGs.
    Returns (buffer, media_type, file_extension).
    """
    
    # Map quality to matrix zoom factor
    # Low: 72 DPI (zoom 1.0)
    # Medium: ~150 DPI (zoom 2.0)
    # High: ~300 DPI (zoom 4.0)
    if quality.lower().startswith("low"):
        zoom = 1.0
    elif quality.lower().startswith("high"):
        zoom = 4.0
    else:
        zoom = 2.0
        
    mat = fitz.Matrix(zoom, zoom)
    
    output_buffer = io.BytesIO()
    
    t0 = time.time()
    doc = fitz.open("pdf", pdf_bytes)
    load_time = time.time() - t0
    logger.info(f"PDF to JPG: doc loaded in {load_time:.3f}s")
    
    num_pages = len(doc)
    
    try:
        if num_pages == 1:
            # Single page -> direct JPG output
            t1 = time.time()
            page = doc[0]
            pix = page.get_pixmap(matrix=mat, alpha=False)
            render_time = time.time() - t1
            
            t2 = time.time()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.save(output_buffer, format="JPEG", quality=85)
            encode_time = time.time() - t2
            
            logger.info(f"PDF to JPG (1 page): render_time={render_time:.3f}s, encode_time={encode_time:.3f}s")
            
            output_buffer.seek(0)
            return output_buffer, "image/jpeg", ".jpg"
            
        else:
            # Multiple pages -> ZIP output
            t_render_total = 0
            t_encode_total = 0
            
            t_zip_start = time.time()
            with zipfile.ZipFile(output_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for i in range(num_pages):
                    t1 = time.time()
                    page = doc[i]
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    t_render_total += (time.time() - t1)
                    
                    t2 = time.time()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Save PIL image to a temporary memory buffer so we can write it to the ZIP
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="JPEG", quality=85)
                    img_bytes = img_buffer.getvalue()
                    t_encode_total += (time.time() - t2)
                    
                    # Write to zip
                    zip_file.writestr(f"page-{i+1}.jpg", img_bytes)
                    
            zip_time = time.time() - t_zip_start
            logger.info(f"PDF to JPG ({num_pages} pages): render_total={t_render_total:.3f}s, encode_total={t_encode_total:.3f}s, zip_time={zip_time:.3f}s")
            
            output_buffer.seek(0)
            return output_buffer, "application/zip", ".zip"

    finally:
        doc.close()
