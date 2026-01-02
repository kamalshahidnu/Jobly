"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config.settings import settings
from .routes import jobs, profile, outreach, documents, analytics, agents, auth, approvals

app = FastAPI(
    title="Jobly API",
    description="AI-powered job search automation platform with multi-user authentication and approval workflows",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - configurable via CORS_ORIGINS environment variable
allowed_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(approvals.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(outreach.router, prefix="/api/v1/outreach", tags=["outreach"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Jobly API"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
