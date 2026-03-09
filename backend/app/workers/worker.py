import os
import sys
import logging
from pathlib import Path
from redis import Redis
from rq import Queue, Connection, get_current_job
from io import BytesIO
import time

# Add the project root to sys.path to allow imports from app
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from app.config import settings
from app.core.redis_client import redis_conn
from app.utils.cleanup import cleanup_old_jobs

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def job_wrapper(func, *args, **kwargs):
    """
    Wraps the service function to handle its output and save it to storage.
    Follows a structured storage pattern: storage/jobs/{job_id}/input and /output.
    """
    job = get_current_job()
    job_id = job.get_id()
    
    logger.info(f"[WORKER] Job {job_id} received for {func.__name__}")
    
    # Initialize metadata
    start_time = time.time()
    job.meta['status'] = 'started'
    job.meta['started_at'] = start_time
    job.save_meta()
    
    logger.info(f"[WORKER] Job {job_id} started")
    
    try:
        # Load files if paths are passed (to avoid changing service logic)
        # We assume if an argument is a string/Path pointing to an existing file, 
        # it might need to be read as bytes for the service.
        # However, to be safe and efficient, we'll let the service functions 
        # handle paths if they already do, or we'll wrap the logic here.
        # FOR PDFsIn5: most services take bytes.
        
        final_args = []
        for arg in args:
            if isinstance(arg, (str, Path)) and os.path.exists(str(arg)) and os.path.isfile(str(arg)):
                with open(arg, "rb") as f:
                    final_args.append(f.read())
            elif isinstance(arg, list):
                # Handle lists of paths (e.g. for merge)
                processed_list = []
                for item in arg:
                    if isinstance(item, (str, Path)) and os.path.exists(str(item)) and os.path.isfile(str(item)):
                        with open(item, "rb") as f:
                            processed_list.append(f.read())
                    else:
                        processed_list.append(item)
                final_args.append(processed_list)
            else:
                final_args.append(arg)

        # Execute service function
        result = func(*final_args, **kwargs)
        
        # Determine the result and optional temp_dir
        if isinstance(result, tuple):
            result_io, temp_dir = result
        else:
            result_io, temp_dir = result, None
            
        # Ensure it's a BytesIO or at least has read()
        if hasattr(result_io, 'seek'):
            result_io.seek(0)
            
        # Prepare output directory
        job_dir = settings.JOBS_STORAGE_DIR / job_id
        output_dir = job_dir / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save output file
        output_path = output_dir / "result.pdf"
        # Handle non-pdf extensions if necessary (rare for this app)
        if hasattr(result_io, 'name') and result_io.name:
            ext = Path(result_io.name).suffix
            if ext:
                output_path = output_dir / f"result{ext}"

        with open(output_path, "wb") as f:
            f.write(result_io.read())
            
        duration = time.time() - start_time
        
        # Update metadata for success
        job.meta['status'] = 'finished'
        job.meta['result_path'] = str(output_path)
        job.meta['completed_at'] = time.time()
        job.meta['processing_time'] = round(duration, 3)
        if temp_dir:
            job.meta['temp_dir'] = str(temp_dir)
            
        job.save_meta()
        
        logger.info(f"[WORKER] Job {job_id} finished in {duration:.3f}s. Result: {output_path}")
        return str(output_path)
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[WORKER] Job {job_id} failed after {duration:.3f}s: {str(e)}")
        
        job.meta['status'] = 'failed'
        job.meta['error'] = str(e)
        job.meta['completed_at'] = time.time()
        job.meta['processing_time'] = round(duration, 3)
        job.save_meta()
        raise e

if __name__ == "__main__":
    # Import RQ components here to avoid top-level fork issues on Windows
    from rq import Connection, Queue, SimpleWorker
    from app.core.redis_client import redis_conn

    # Attempt a quick cleanup on startup
    try:
        from app.utils.cleanup import cleanup_old_jobs
        cleanup_old_jobs()
    except Exception as e:
        logger.error(f"Startup cleanup failed: {e}")

    with Connection(redis_conn):
        # On Windows, we use SimpleWorker as it doesn't use fork()
        worker = SimpleWorker(Queue("pdf_tasks"))
        logger.info("Worker started (SimpleWorker), listening on 'pdf_tasks' queue.")
        worker.work()
