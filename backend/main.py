from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="ProjectPilot API",
    description="AI-powered project analysis and feasibility assessment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api/v1 prefix
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("ProjectPilot API starting up...")
    logger.info("Using in-memory storage (no database)")
    logger.info("API running at http://localhost:8080")
    logger.info("API Docs available at http://localhost:8080/docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ProjectPilot API shutting down...")

@app.get("/")
async def root():
    return {
        "message": "ProjectPilot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
