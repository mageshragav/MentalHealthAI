# Build stage
FROM python:3.12-slim AS builder

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Copy pyproject.toml and uv.lock for dependency resolution
COPY backend/pyproject.toml backend/uv.lock ./

# Install Python dependencies
RUN uv pip install --no-cache -r pyproject.toml


# Runtime stage
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

WORKDIR /app

# Install system dependencies (runtime only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make scripts in .local/bin available in PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy application code
COPY backend ./backend
COPY frontend ./frontend
COPY .gitignore .dockerignore ./

# Create necessary directories for persistence
RUN mkdir -p /app/backend/data/chroma_db /app/backend/logs && \
    chmod -R 777 /app/backend/data /app/backend/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 8501

# Default command (can be overridden in docker-compose)
CMD ["python", "backend/main.py"]
