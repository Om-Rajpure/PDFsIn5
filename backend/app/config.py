import os
from pathlib import Path

class Settings:
    # Use environment variables with sensible defaults
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://pdfsin5.com")
    
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Storage configuration
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    JOBS_STORAGE_DIR: Path = STORAGE_DIR / "jobs"
    
    # 100 MB default (updated per requirement for large file support)
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 100))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Cleanup file lifetime in minutes (default 30)
    TEMP_FILE_LIFETIME_MINUTES: int = int(os.getenv("TEMP_FILE_LIFETIME_MINUTES", 30))

    # Job Timeouts (in seconds)
    TIMEOUTS = {
        "merge-pdf": 60,
        "split-pdf": 60,
        "compress-pdf": 90,
        "watermark-pdf": 60,
        "ocr-pdf": 300,
        "redact-pdf": 120,
        "default": 60
    }

settings = Settings()

# Ensure core storage directories exist
settings.STORAGE_DIR.mkdir(exist_ok=True)
settings.JOBS_STORAGE_DIR.mkdir(exist_ok=True)
