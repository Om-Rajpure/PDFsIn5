import os
import uuid
import shutil
import aiofiles
from fastapi import UploadFile

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def save_upload(file: UploadFile) -> dict:
    """
    Save an uploaded file to the uploads/ directory.
    Returns a dict with the saved path and unique filename.
    """
    ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, unique_name)

    async with aiofiles.open(save_path, "wb") as out:
        content = await file.read()
        await out.write(content)

    return {
        "original_filename": file.filename,
        "saved_as": unique_name,
        "path": save_path,
        "size_bytes": len(content),
    }


def delete_file(filepath: str) -> bool:
    """Delete a file from the filesystem."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except OSError:
        pass
    return False


def move_to_output(src_path: str) -> str:
    """Move a processed file to the outputs/ directory."""
    filename = os.path.basename(src_path)
    dest = os.path.join(OUTPUT_DIR, filename)
    shutil.move(src_path, dest)
    return dest
