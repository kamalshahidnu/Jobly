# Root Dockerfile for AWS App Runner (monorepo-friendly).
# It builds and runs the FastAPI backend located in ./backend

FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

WORKDIR /app

# Copy dependency files first for better Docker layer caching
COPY backend/pyproject.toml backend/poetry.lock ./

# Configure poetry to not create virtual env (we're in a container)
RUN poetry config virtualenvs.create false

# Install only runtime dependencies (do not try to install the project package yet)
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Copy backend application code
COPY backend/ ./

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Create necessary directories with proper permissions
RUN mkdir -p data logs credentials && \
    chown -R appuser:appuser data logs credentials

USER appuser

# App Runner will route traffic to the container port you configure (commonly 8000).
EXPOSE 8000

# Run the application (honor $PORT if the platform sets it)
CMD ["sh", "-c", "uvicorn jobly.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


