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
from app.config import settings

logger = logging.getLogger(__name__)

# Configuration
MAX_AGE_SECONDS   = settings.TEMP_FILE_LIFETIME_MINUTES * 60
POLL_INTERVAL_SEC = 5  * 60   # poll every 5 minutes


def _delete_old_files(*directories: Path) -> int:
    """
    Delete files older than MAX_AGE_SECONDS in the given directories.
    Returns the count of deleted files.
    """
    import time
    now     = time.time()
    deleted = 0

    for directory in directories:
        if not directory.is_dir():
            continue
        for filepath in directory.iterdir():
            if not filepath.is_file():
                continue
            try:
                age = now - filepath.stat().st_mtime
                if age > MAX_AGE_SECONDS:
                    filepath.unlink()
                    deleted += 1
                    logger.debug("Deleted old file: %s (age %.0fs)", filepath, age)
            except Exception as exc:
                logger.warning("Could not delete %s: %s", filepath, exc)

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
            count = _delete_old_files(*directories)
            if count:
                logger.info("Cleanup pass: deleted %d old file(s).", count)
        except Exception as exc:
            logger.error("Cleanup pass failed: %s", exc)
        await asyncio.sleep(POLL_INTERVAL_SEC)
