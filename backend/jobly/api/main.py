"""FastAPI application main entry point (disabled for Phase 1)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import jobs, profile, outreach, documents, analytics, agents

# This will be enabled in Phase 2
# For now, we're focusing on Streamlit UI

app = FastAPI(
    title="Jobly API",
    description="AI-powered job search automation platform",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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
