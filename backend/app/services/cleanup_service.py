"""
cleanup_service.py
------------------
Background cleanup task that removes files older than MAX_AGE_MINUTES
from the uploads/ and outputs/ folders.

Run via the FastAPI lifespan event (started in main.py).
"""

import os
import asyncio
import logging
from pathlib import Path
import shutil
import time
from app.config import settings

logger = logging.getLogger(__name__)

# Configuration
MAX_AGE_SECONDS   = settings.TEMP_FILE_LIFETIME_MINUTES * 60
POLL_INTERVAL_SEC = 5  * 60   # poll every 5 minutes


def _delete_old_items(*paths: Path) -> int:
    """
    Delete files or directories older than MAX_AGE_SECONDS in the given paths.
    Returns the count of deleted items.
    """
    now     = time.time()
    deleted = 0

    for path in paths:
        if not path.exists():
            continue
            
        if path.is_dir():
            # For the root storage directories (uploads, outputs, jobs), 
            # we iterate through their children.
            for item in path.iterdir():
                try:
                    # Use directory mtime for job folders
                    mtime = item.stat().st_mtime
                    age = now - mtime
                    if age > MAX_AGE_SECONDS:
                        if item.is_file() or item.is_symlink():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        deleted += 1
                        logger.debug("Deleted old item: %s (age %.0fs)", item, age)
                except Exception as exc:
                    logger.warning("Could not delete %s: %s", item, exc)
        elif path.is_file():
            # Handle if a single file was passed (unlikely but safe)
            try:
                age = now - path.stat().st_mtime
                if age > MAX_AGE_SECONDS:
                    path.unlink()
                    deleted += 1
            except Exception:
                pass

    return deleted


async def run_cleanup_loop(*directories: Path) -> None:
    """
    Continuously polls and cleans up old files.
    Designed to run as a background asyncio task.
    """
    logger.info(
        "File cleanup daemon started — max age %ds, poll every %ds",
        MAX_AGE_SECONDS,
        POLL_INTERVAL_SEC,
    )
    while True:
        try:
            count = _delete_old_items(*directories)
            if count:
                logger.info("Cleanup pass: deleted %d old item(s).", count)
        except Exception as exc:
            logger.error("Cleanup pass failed: %s", exc)
        await asyncio.sleep(POLL_INTERVAL_SEC)
