# Multi-stage build for Cloud Run optimized deployment
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml .

# Install dependencies using uv (fastest Python package installer)
RUN uv pip install --system --no-cache .

# Copy application code
COPY . .

# Production stage - minimal image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application code
COPY . .

# Create non-root user for security (Cloud Run requirement)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Run the application
# Cloud Run will inject GCP_PROJECT_ID and credentials automatically
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level info
