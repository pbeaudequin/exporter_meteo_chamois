# Multi-stage build for optimized production image
# Stage 1: Builder
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Set labels for metadata
LABEL maintainer="Philippe Beaudequin"
LABEL description="Prometheus exporter for Meteo Roquefort les Pins weather station"
LABEL version="1.0.0"

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash exporter

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/exporter/.local

# Copy application code
COPY src/ /app/src/

# Change ownership to non-root user
RUN chown -R exporter:exporter /app

# Switch to non-root user
USER exporter

# Add local bin to PATH
ENV PATH=/home/exporter/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 9100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9100/health')"

# Run with gunicorn for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:9100", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "src.app:create_app()"]
