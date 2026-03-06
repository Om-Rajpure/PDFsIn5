import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tools

app = FastAPI(
    title="PDFsIn5 API",
    description="Backend API for the PDFsIn5 document processing platform.",
    version="1.0.0",
)

# Allow requests from the Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools.router, prefix="/api", tags=["tools"])


@app.get("/")
async def root():
    return {"message": "Welcome to the PDFsIn5 API", "docs": "/docs"}
