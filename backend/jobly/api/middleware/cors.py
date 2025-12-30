"""CORS middleware configuration."""

from fastapi.middleware.cors import CORSMiddleware
from typing import List


def setup_cors(app, origins: List[str] = None):
    """Setup CORS middleware.

    Args:
        app: FastAPI application
        origins: List of allowed origins
    """
    if origins is None:
        origins = [
            "http://localhost:3000",  # React dev server
            "http://localhost:8000",  # FastAPI default port
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
