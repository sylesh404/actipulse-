"""FastAPI Backend for ActiPulse AI - Premium Sports-Tech Platform."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
import logging
from datetime import date, datetime

from database.database import DatabaseManager
from backend.api import (
    activity_routes,
    analytics_routes,
    comparison_routes,
    timeline_routes,
    pattern_routes,
    ai_routes,
    report_routes,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ActiPulse AI API",
    description="Premium Sports-Tech Activity Intelligence Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    """Dependency to get database manager instance."""
    db = DatabaseManager()
    db.initialize_schema()
    return db

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 ActiPulse AI FastAPI Backend Starting...")
    db = DatabaseManager()
    db.initialize_schema()
    logger.info("✅ Database initialized")
    logger.info("✅ FastAPI server ready")

@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "app": "ActiPulse AI",
        "version": "2.0.0",
        "status": "online",
        "architecture": "React + FastAPI + SQLite",
        "ai_providers": ["Groq", "Gemini"],
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = DatabaseManager()
        db.initialize_schema()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )

# Include routers
app.include_router(activity_routes.router, prefix="/api/activities", tags=["Activities"])
app.include_router(analytics_routes.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(comparison_routes.router, prefix="/api/comparison", tags=["Comparison"])
app.include_router(timeline_routes.router, prefix="/api/timeline", tags=["Timeline"])
app.include_router(pattern_routes.router, prefix="/api/patterns", tags=["Pattern Detection"])
app.include_router(ai_routes.router, prefix="/api/ai", tags=["AI Services"])
app.include_router(report_routes.router, prefix="/api/reports", tags=["Reports"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
