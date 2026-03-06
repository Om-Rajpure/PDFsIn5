import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import tools
from app.services.cleanup_service import run_cleanup_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ── Directories ───────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Rate limiter (shared across all routes) ───────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

# ── Lifespan: start cleanup daemon ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background services on startup; cleanly stop on shutdown."""
    cleanup_task = asyncio.create_task(
        run_cleanup_loop(UPLOAD_DIR, OUTPUT_DIR)
    )
    logger.info("Background cleanup daemon started.")
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("Background cleanup daemon stopped.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PDFsIn5 API",
    description="Backend API for the PDFsIn5 document processing platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow Vite dev server and dynamic production origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handlers ─────────────────────────────────────────────────────
@app.exception_handler(413)
async def file_too_large_handler(request: Request, exc):
    return JSONResponse(
        status_code=413,
        content={"detail": "File is too large. Maximum allowed size is 50 MB."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


# ── Router ────────────────────────────────────────────────────────────────────
app.include_router(tools.router, prefix="/api", tags=["tools"])


# ── Sitemap ───────────────────────────────────────────────────────────────────
@app.get("/sitemap.xml")
async def sitemap():
    """Dynamically generates an XML sitemap for SEO."""
    base_url = "https://pdfsin5.com"
    
    # Core pages
    urls = [
        {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{base_url}/blog", "changefreq": "weekly", "priority": "0.8"},
    ]
    
    # Tool pages (derived from the frontend TOOLS list)
    tools = [
        "merge-pdf", "split-pdf", "rotate-pdf", "organize-pages", "add-page-numbers", "crop-pdf",
        "pdf-to-word", "pdf-to-excel", "pdf-to-jpg", "word-to-pdf", "excel-to-pdf", "ppt-to-pdf", "images-to-pdf",
        "compress-pdf", "repair-pdf", "protect-pdf", "unlock-pdf", "watermark-pdf", "redact-pdf",
        "ocr-pdf", "compare-pdf", "scan-to-pdf", "translate-pdf"
    ]
    for tool in tools:
        urls.append({"loc": f"{base_url}/tool/{tool}", "changefreq": "monthly", "priority": "0.9"})
        
    # Blog posts
    posts = ["how-to-merge-pdf", "how-to-compress-pdf"]
    for post in posts:
        urls.append({"loc": f"{base_url}/blog/{post}", "changefreq": "monthly", "priority": "0.7"})

    xml_urls = "".join([
        f"<url><loc>{u['loc']}</loc><changefreq>{u['changefreq']}</changefreq><priority>{u['priority']}</priority></url>"
        for u in urls
    ])
    
    sitemap_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{xml_urls}\n</urlset>'
    
    return Response(content=sitemap_xml, media_type="application/xml")


@app.get("/")
async def root():
    return {"message": "Welcome to the PDFsIn5 API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
