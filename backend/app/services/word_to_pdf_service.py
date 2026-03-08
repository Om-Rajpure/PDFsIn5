import time
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)

def word_to_pdf_service(file_bytes: bytes, original_filename: str) -> Tuple[str, List[str], dict]:
    """
    Converts a Word document to a PDF file cross-platform using LibreOffice in headless mode.
    Returns (pdf_path, temp_files_paths_to_cleanup, timing_logs).
    """
    timings = {}
    temp_files = []
    
    t0 = time.time()
    
    # Create temp working directory
    temp_dir = tempfile.mkdtemp()
    temp_dir_path = Path(temp_dir)
    
    # Fallback to .docx if no valid extension is found
    ext = Path(original_filename).suffix.lower()
    if ext not in [".docx", ".doc"]:
        ext = ".docx"
        
    # The prompt explicitly asks to use original filename.
    # However, to avoid issues with spaces or special characters in original filename with subprocess,
    # we'll use "input.docx" as requested precisely in the user prompt example.
    input_filename = f"input{ext}"
    docx_path = temp_dir_path / input_filename
    
    with open(docx_path, "wb") as f:
        f.write(file_bytes)
        
    temp_files.append(str(docx_path))
    
    parse_time = time.time() - t0
    timings["save_time"] = parse_time
    logger.info(f"Word to PDF: DOCX saved in {parse_time:.3f}s")
    
    t_gen_start = time.time()
    
    # The output pdf will be named input.pdf based on the input filename.
    pdf_path = temp_dir_path / "input.pdf"
    
    # Command array exactly matching requested format
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        input_filename,
        "--outdir", str(temp_dir_path)
    ]
    
    try:
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(temp_dir_path) # Critical: Run inside temp directory
        )
        
        if process.returncode != 0:
            logger.error(f"LibreOffice failed: {process.stderr.decode()}")
            raise Exception("LibreOffice conversion failed.")
            
        if not pdf_path.exists():
            raise Exception("LibreOffice succeeded but PDF was not generated. Please check LibreOffice installation.")
            
        # We append pdf_path and temp_dir_path for cleanup
        temp_files.append(str(pdf_path))
        temp_files.append(str(temp_dir_path)) 
        
        gen_time = time.time() - t_gen_start
        timings["conversion_time"] = gen_time
        logger.info(f"Word to PDF: LibreOffice PDF generated in {gen_time:.3f}s")
        
        return str(pdf_path), temp_files, timings
        
    except FileNotFoundError:
        # libreoffice is not found in PATH
        logger.error("Word to PDF: LibreOffice is not installed or not found in system PATH.")
        raise Exception("LibreOffice is not installed on the server. Please install LibreOffice to use this feature.")
    except Exception as e:
        logger.exception("Word to PDF: Conversion process threw an error.")
        raise Exception(f"Document conversion failed critically: {str(e)}")
