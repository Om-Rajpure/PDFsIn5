import os
import time
import shutil
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

def cleanup_old_jobs():
    """
    Scans the storage/jobs directory and removes folders older than
    TEMP_FILE_LIFETIME_MINUTES.
    """
    jobs_dir = Path(settings.JOBS_STORAGE_DIR)
    if not jobs_dir.exists():
        return

    now = time.time()
    # Convert minutes to seconds
    lifetime_seconds = settings.TEMP_FILE_LIFETIME_MINUTES * 60
    
    deleted_count = 0
    error_count = 0

    try:
        # Iterate through each job directory
        for job_path in jobs_dir.iterdir():
            if not job_path.is_dir():
                continue

            # Check the modification time of the directory itself
            # or the most recent file inside? 
            # Directory mtime usually updates when files are added/removed.
            mtime = job_path.stat().st_mtime
            age = now - mtime

            if age > lifetime_seconds:
                try:
                    logger.info(f"Cleaning up old job: {job_path.name} (age: {age/60:.1f} mins)")
                    shutil.rmtree(job_path)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete job dir {job_path}: {e}")
                    error_count += 1

    except Exception as e:
        logger.error(f"Error during jobs cleanup: {e}")

    if deleted_count > 0:
        logger.info(f"Cleanup complete. Deleted {deleted_count} job directories. Errors: {error_count}")

if __name__ == "__main__":
    # Setup basic logging if run directly
    logging.basicConfig(level=logging.INFO)
    cleanup_old_jobs()
