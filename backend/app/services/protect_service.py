"""
protect_service.py
-------------------
Protects a PDF using pikepdf AES-256 encryption.
"""

import io
import os
import shutil
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

def protect_pdf_service(file_bytes: bytes, password: str) -> tuple[io.BytesIO, str]:
    """
    Protect a PDF with a password.
    
    Args:
        file_bytes: Raw bytes of the input PDF.
        password: Password string.
    
    Returns:
        A tuple of (io.BytesIO consisting of protected file, temp directory path string).
        The temporary directory needs to be cleaned up by the caller.
    """
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")
    
    if len(file_bytes) < 4 or not file_bytes.startswith(b"%PDF"):
        raise ValueError("Uploaded file is not a valid PDF document.")
        
    if not password:
        raise ValueError("Password cannot be empty.")
        
    start_time = time.time()
    logger.info(f"Starting PDF encryption. Size: {len(file_bytes) / (1024 * 1024):.2f} MB")

    temp_dir = tempfile.mkdtemp()
    input_file_path = os.path.join(temp_dir, "input.pdf")
    output_file_path = os.path.join(temp_dir, "protected.pdf")
    
    try:
        t_save_start = time.time()
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File save time: {time.time() - t_save_start:.3f}s")
        
        t_encrypt_start = time.time()
        try:
            import pikepdf
            with pikepdf.Pdf.open(input_file_path) as pdf:
                # Disallow modifying, allow printing
                permissions = pikepdf.Permissions(
                    extract=True,
                    modify_other=False,
                    modify_assembly=False,
                    modify_form=False,
                    modify_annotation=False,
                    print_lowres=True,
                    print_highres=True,
                )
                encryption = pikepdf.Encryption(
                    user=password,
                    owner=password,
                    allow=permissions
                )
                pdf.save(output_file_path, encryption=encryption)
        except Exception as e:
            logger.exception(f"Exception while encrypting PDF: {str(e)}")
            raise ValueError(f"Encryption failed. The file may be corrupted or already encrypted: {str(e)}")
            
        encryption_time = time.time() - t_encrypt_start
        logger.info(f"Encryption execution time: {encryption_time:.3f}s")
            
        if not os.path.exists(output_file_path) or os.path.getsize(output_file_path) == 0:
            raise ValueError("Encryption engine did not produce output file or file is empty")
            
        with open(output_file_path, "rb") as f:
            protected_bytes = f.read()
            
        buffer = io.BytesIO(protected_bytes)
        buffer.seek(0)
        
        total_time = time.time() - start_time
        logger.info(f"Total encryption process completed in {total_time:.3f}s.")
        
        return buffer, temp_dir
        
    except ValueError as ve:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ve
    except Exception as e:
        logger.exception(f"Unexpected error during PDF protection: {str(e)}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ValueError("An unexpected error occurred during encryption. Please try again.")
