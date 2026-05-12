"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from app.database import init_db
from app.routes import papers, questions, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting SSC PDF Analyzer...")
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down SSC PDF Analyzer...")

# Create FastAPI app
app = FastAPI(
    title="SSC PDF Analyzer API",
    description="AI-powered PDF analyzer for SSC aspirants",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to SSC PDF Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "papers": "/api/papers",
            "questions": "/api/questions",
            "analytics": "/api/analytics"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
