# Production Multi-Stage Dockerfile for TripSync AI Backend
# Optimized for Render Free Tier (Single worker, <512MB RAM resident memory)

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.11-slim as runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed wheels
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code and ML pipeline artifacts
COPY backend /app/backend
COPY ml_pipeline /app/ml_pipeline

# Set environment
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

EXPOSE 8000

# Run with 1 worker to strictly respect the 512 MB RAM free tier budget
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
