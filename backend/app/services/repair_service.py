"""
repair_service.py
-------------------
Repairs a corrupted or problematic PDF using Ghostscript.
"""

import io
import os
import shutil
import tempfile
import logging
import subprocess
import time

logger = logging.getLogger(__name__)

def repair_pdf_service(file_bytes: bytes) -> tuple[io.BytesIO, str]:
    """
    Repair a PDF using Ghostscript.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
    
    Returns:
        A tuple of (io.BytesIO consisting of repaired file, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    start_time = time.time()
    logger.info(f"Starting PDF repair on file of size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    # Detect Ghostscript Properly
    gs_executable = shutil.which("gs") or shutil.which("gswin64c")
    if not gs_executable:
        logger.error("Ghostscript executable ('gs' or 'gswin64c') not found.")
        raise ValueError("Ghostscript repair engine is not installed on this server.")

    # Safe File Handling
    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    output_file_path = os.path.join(temp_dir, "repaired.pdf")
    
    try:
        t_save_start = time.time()
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File save time: {time.time() - t_save_start:.3f}s")
            
        command = [
            gs_executable,
            "-q",
            "-dNOPAUSE",
            "-dBATCH",
            "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-dPDFSETTINGS=/prepress",
            f"-sOutputFile={output_file_path}",
            input_file_path
        ]
        
        logger.info(f"Executing Ghostscript command: {' '.join(command)}")
        
        t_repair_start = time.time()
        try:
            process = subprocess.run(command, capture_output=True, text=True)
            logger.info(f"Ghostscript stdout: {process.stdout}")
            if process.stderr:
                logger.warning(f"Ghostscript stderr: {process.stderr}")
                
            if process.returncode != 0:
                logger.error(f"Ghostscript repair failed with code {process.returncode}")
                # We do not immediately raise here, we check if output file was somehow produced
        except Exception as e:
            logger.exception(f"Exception while running Ghostscript: {str(e)}")
            raise ValueError(f"Repair engine encountered an error: {str(e)}")
            
        repair_execution_time = time.time() - t_repair_start
        logger.info(f"Repair execution time: {repair_execution_time:.3f}s")
            
        # Verify Output File
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            logger.error("Ghostscript did not produce output file or file is empty")
            if 'process' in locals() and process.stderr:
                logger.error(f"Failure reason: {process.stderr}")
            raise ValueError("Failed to repair PDF. The file may be too severely corrupted or encrypted.")
            
        with open(output_file_path, "rb") as f:
            repaired_bytes = f.read()
            
        # Streaming Response preparation
        buffer = io.BytesIO(repaired_bytes)
        buffer.seek(0)
        
        total_time = time.time() - start_time
        logger.info(f"Total repair process completed in {total_time:.3f}s. Final size: {len(repaired_bytes) / (1024 * 1024):.2f} MB")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        # Re-raise known value errors (which get shown directly to the user as 400 Bad Request)
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        # In case of any unhandled error, clean up the temp dir immediately because we won't return it
        logger.exception(f"Unexpected error during PDF repair: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error occurred during repair. Please try again.")
