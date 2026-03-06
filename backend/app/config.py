import os

class Settings:
    # Use environment variables with sensible defaults
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://pdfsin5.com")
    
    # 50 MB default
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 50))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Cleanup file lifetime in minutes (default 30)
    TEMP_FILE_LIFETIME_MINUTES: int = int(os.getenv("TEMP_FILE_LIFETIME_MINUTES", 30))

settings = Settings()
