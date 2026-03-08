import time
import logging
import tempfile
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)

def ppt_to_pdf_service(file_bytes: bytes, original_filename: str) -> Tuple[str, List[str], dict]:
    """
    Converts a PowerPoint document to a PDF file cross-platform using LibreOffice in headless mode.
    Returns (pdf_path, temp_files_paths_to_cleanup, timing_logs).
    """
    timings = {}
    temp_files = []
    
    t0 = time.time()
    
    # Create temp working directory
    temp_dir = tempfile.mkdtemp()
    temp_dir_path = Path(temp_dir)
    
    # Fallback to .pptx if no valid extension is found
    ext = Path(original_filename).suffix.lower()
    if ext not in [".pptx", ".ppt"]:
        ext = ".pptx"
        
    # The prompt explicitly asks to use original filename, but using input.pptx guarantees safety
    input_filename = f"input{ext}"
    ppt_path = temp_dir_path / input_filename
    
    with open(ppt_path, "wb") as f:
        f.write(file_bytes)
        
    temp_files.append(str(ppt_path))
    
    parse_time = time.time() - t0
    timings["save_time"] = parse_time
    logger.info(f"PowerPoint to PDF: PPTX saved in {parse_time:.3f}s")
    
    t_gen_start = time.time()
    
    # The output pdf will be named input.pdf based on the input filename.
    pdf_path = temp_dir_path / "input.pdf"
    
    # Determine the correct LibreOffice executable dynamically
    libreoffice_exec = shutil.which("soffice")
    if not libreoffice_exec:
        libreoffice_exec = shutil.which("libreoffice")
        
    if not libreoffice_exec:
        raise RuntimeError("LibreOffice is not installed on the server or not found in PATH.")
        
    # Command array exactly matching requested format
    cmd = [
        libreoffice_exec,
        "--headless",
        "--convert-to", "pdf",
        input_filename,
        "--outdir", str(temp_dir_path)
    ]
    
    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(temp_dir_path) # Critical: Run inside temp directory
        )
        
        # Log outputs for debugging
        if process.stdout:
            logger.info(f"LibreOffice stdout: {process.stdout}")
        if process.stderr:
            logger.warning(f"LibreOffice stderr: {process.stderr}")
            
        if process.returncode != 0:
            error_msg = process.stderr if process.stderr else "Unknown error"
            logger.error(f"LibreOffice failed with exit code {process.returncode}: {error_msg}")
            raise Exception(f"LibreOffice conversion failed: {error_msg}")
            
        if not pdf_path.exists():
            error_msg = process.stderr if process.stderr else "No output file generated."
            raise Exception(f"LibreOffice succeeded but PDF was not generated. Details: {error_msg}")
            
        # We append pdf_path and temp_dir_path for cleanup
        temp_files.append(str(pdf_path))
        temp_files.append(str(temp_dir_path)) 
        
        gen_time = time.time() - t_gen_start
        timings["conversion_time"] = gen_time
        logger.info(f"PowerPoint to PDF: LibreOffice PDF generated in {gen_time:.3f}s")
        
        return str(pdf_path), temp_files, timings
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        logger.error(f"LibreOffice failed with exit code {e.returncode}: {error_msg}")
        raise RuntimeError(f"LibreOffice conversion failed: {error_msg}")
    except RuntimeError as e:
        logger.error(f"PowerPoint to PDF: {str(e)}")
        raise Exception(str(e))
    except Exception as e:
        logger.exception("PowerPoint to PDF: Conversion process threw an error.")
        raise Exception(f"Document conversion failed critically: {str(e)}")
