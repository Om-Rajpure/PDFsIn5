import multiprocessing
import sys
import logging
import os
from pathlib import Path

# Monkeypatch multiprocessing to handle 'fork' on Windows
# This addresses some RQ versions attempting to use 'fork' context by default
if sys.platform == 'win32':
    orig_get_context = multiprocessing.get_context
    def patched_get_context(method=None):
        if method == 'fork':
            try:
                return orig_get_context('spawn')
            except ValueError:
                return orig_get_context()
        return orig_get_context(method)
    multiprocessing.get_context = patched_get_context

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Now safe to import RQ
from rq import Connection, Queue, SimpleWorker
from app.config import settings
from app.core.redis_client import redis_conn
from app.utils.cleanup import cleanup_old_jobs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Windows Worker starting...")
    
    # Attempt a quick cleanup on startup
    try:
        cleanup_old_jobs()
    except Exception as e:
        logger.error(f"Startup cleanup failed: {e}")

    try:
        with Connection(redis_conn):
            # On Windows, we MUST use SimpleWorker
            worker = SimpleWorker(Queue("pdf_tasks"))
            logger.info("Worker started (SimpleWorker), listening on 'pdf_tasks' queue.")
            worker.work()
    except Exception as e:
        logger.critical(f"Worker crashed: {e}")
        sys.exit(1)
