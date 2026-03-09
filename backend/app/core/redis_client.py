import os
from redis import Redis
from rq import Queue
from app.config import settings

# Initialize Redis connection
redis_conn = Redis.from_url(settings.REDIS_URL)

# Define the queue for PDF tasks
pdf_queue = Queue("pdf_tasks", connection=redis_conn)
