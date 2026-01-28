"""
Smart ATS System - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import models, analysis, reconstruction

# Create FastAPI app
app = FastAPI(
    title="Smart ATS API",
    description="AI-powered CV analysis and reconstruction system",
    version="2.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(models.router)
app.include_router(analysis.router)
app.include_router(reconstruction.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Smart ATS API is running",
        "version": "2.1.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "ai_providers": True,
            "cv_processor": True
        }
    }
