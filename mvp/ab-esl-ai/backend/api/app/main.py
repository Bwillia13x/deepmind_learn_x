"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    logger.info(f"ASR enabled: {settings.enable_asr}")
    logger.info(f"LLM enabled: {settings.enable_llm}")
    
    # Initialize database tables
    from app.services.db import init_db
    try:
        init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered tools for ESL education in Alberta schools",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["http://localhost:3001"],  # Include student app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (disabled in test environment)
if os.getenv("TESTING") != "true" and settings.environment != "test":
    from app.core.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(api_router)
