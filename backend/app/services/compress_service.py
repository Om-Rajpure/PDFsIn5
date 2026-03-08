"""
compress_service.py
-------------------
Compresses a PDF using Ghostscript presets.
"""

import io
import os
import shutil
import tempfile
import logging
import subprocess
import time

logger = logging.getLogger(__name__)

# Presets from lowest compression (best quality) to highest compression (lowest quality)
GHOSTSCRIPT_PRESETS = [
    "/printer",
    "/ebook",
    "/screen"
]

def compress_pdf_service(file_bytes: bytes, target_size_mb: float = None) -> tuple[io.BytesIO, str]:
    """
    Compress a PDF using Ghostscript.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
        target_size_mb: Optional target size in MB.
    
    Returns:
        A tuple of (io.BytesIO consisting of compressed file, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    # Step 4: Validate Input File
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    start_time = time.time()
    original_size = len(file_bytes)
    original_size_mb = original_size / (1024 * 1024)
    logger.info(f"Starting PDF compression. Original size: {original_size_mb:.2f} MB, Target size: {target_size_mb} MB")

    # Step 1: Detect Ghostscript Properly
    gs_executable = shutil.which("gs") or shutil.which("gswin64c")
    if not gs_executable:
        logger.error("Ghostscript executable ('gs' or 'gswin64c') not found.")
        raise ValueError("Ghostscript compression engine is not installed on this server.")

    if target_size_mb is not None and original_size_mb <= target_size_mb:
        logger.info(f"Original file is already smaller than target ({target_size_mb} MB). Returning original file.")
        buffer = io.BytesIO(file_bytes)
        buffer.seek(0)
        return buffer, None
        
    # Step 6: Safe File Handling
    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    output_file_path = os.path.join(temp_dir, "output.pdf")
    
    try:
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
            
        best_output_path = None
        best_size = float('inf')
        
        presets_to_try = GHOSTSCRIPT_PRESETS if target_size_mb is not None else ["/screen"]
        
        for preset in presets_to_try:
            logger.info(f"Trying Ghostscript compression preset: {preset}")
            
            command = [
                gs_executable,
                "-q",
                "-dNOPAUSE",
                "-dBATCH",
                "-dSAFER",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                f"-dPDFSETTINGS={preset}",
                f"-sOutputFile={output_file_path}",
                input_file_path
            ]
            
            # Step 2: Add Debug Logging
            logger.info(f"Executing Ghostscript command: {' '.join(command)}")
            
            try:
                # Step 3: Protect Against Crashes
                process = subprocess.run(command, capture_output=True, text=True)
                logger.info(f"Ghostscript stdout: {process.stdout}")
                if process.stderr:
                    logger.warning(f"Ghostscript stderr: {process.stderr}")
                    
                if process.returncode != 0:
                    logger.error(f"Ghostscript compression failed with code {process.returncode} for preset {preset}")
                    continue
            except Exception as e:
                logger.exception(f"Exception while running Ghostscript: {str(e)}")
                raise ValueError(f"Compression engine encountered an error: {str(e)}")
                
            # Step 5: Verify Output File
            if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
                logger.error(f"Ghostscript did not produce output file for preset {preset} or file is empty")
                if 'process' in locals() and process.stderr:
                    logger.error(f"Failure reason: {process.stderr}")
                continue
                
            compressed_size = os.path.getsize(output_file_path)
            compressed_size_mb = compressed_size / (1024 * 1024)
            logger.info(f"Preset {preset} produced file of size {compressed_size_mb:.2f} MB")
            
            # Save the result
            if best_output_path and os.path.exists(best_output_path):
                os.remove(best_output_path)
                
            best_output_path = os.path.join(temp_dir, f"best_output_{preset.replace('/', '')}.pdf")
            os.rename(output_file_path, best_output_path)
            best_size = compressed_size
            
            if target_size_mb is not None and compressed_size_mb <= target_size_mb:
                logger.info(f"Target size reached ({compressed_size_mb:.2f} MB <= {target_size_mb} MB). Stopping compression routine.")
                break
                
        if not best_output_path or not os.path.exists(best_output_path):
            logger.error("All compression attempts failed. Ghostscript could not process the file.")
            raise ValueError("Failed to compress PDF. Please check if the PDF is encrypted or corrupted.")
            
        with open(best_output_path, "rb") as f:
            compressed_bytes = f.read()
            
        # Step 7 & 8: Streaming Response & Cleanup prep
        buffer = io.BytesIO(compressed_bytes)
        buffer.seek(0)
        
        compression_time = time.time() - start_time
        logger.info(f"Compression completed in {compression_time:.2f}s. Final size: {best_size / (1024 * 1024):.2f} MB")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        # Re-raise known value errors (which get shown directly to the user as 400 Bad Request)
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        # In case of any unhandled error, clean up the temp dir immediately because we won't return it
        logger.exception(f"Unexpected error during PDF compression: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error occurred during compression. Please try again.")
