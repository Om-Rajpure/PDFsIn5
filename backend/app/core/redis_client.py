import logging
from redis import Redis
from rq import Queue
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis connection safely
try:
    redis_conn = Redis.from_url(settings.REDIS_URL, socket_timeout=5)
    # Ping to verify connection
    redis_conn.ping()
    logger.info(f"Successfully connected to Redis at {settings.REDIS_URL.split('@')[-1]}")
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}. Jobs will fail but API will start.")
    redis_conn = None

# Define the queue for PDF tasks
pdf_queue = Queue("pdf_tasks", connection=redis_conn) if redis_conn else None
