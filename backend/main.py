"""
GraphLens Backend — FastAPI Application Entry Point.

This file creates the FastAPI application instance, configures
middleware, and includes all API routers.

What is FastAPI?
FastAPI is a modern Python web framework built on top of:
- Starlette (for HTTP/WebSocket handling)
- Pydantic (for data validation)
- Uvicorn (ASGI server)

It auto-generates OpenAPI documentation at /docs (Swagger UI)
and /redoc (ReDoc), which means your API is self-documenting.

Interview Q: "What is CORS and why do we need it?"
Answer: Browsers enforce Same-Origin Policy — JavaScript on
localhost:5173 cannot fetch from localhost:8000 by default.
CORS middleware tells the browser "yes, this origin is allowed".
Without it, every frontend API call would be blocked.

How to run:
    uvicorn backend.main:app --reload --port 8000
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import (
    graph_router,
    node_router,
    timeline_router,
    analytics_router,
    simulation_router,
    prediction_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="GraphLens API",
    description=(
        "MLOps Intelligence Platform — Graph-based failure analysis, "
        "temporal replay, and predictive analytics for ML pipelines."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(graph_router.router)
app.include_router(node_router.router)
app.include_router(timeline_router.router)
app.include_router(analytics_router.router)
app.include_router(simulation_router.router)
app.include_router(prediction_router.router)


@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "GraphLens API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("=" * 60)
    logger.info("GraphLens API starting up")
    logger.info(f"Data directory: {settings.data_path}")
    logger.info(f"CORS origins: {settings.cors_origins}")
    logger.info(f"Docs available at: http://{settings.host}:{settings.port}/docs")
    logger.info("=" * 60)
