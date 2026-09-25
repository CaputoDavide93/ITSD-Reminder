# Multi-architecture Dockerfile for ITSD Reminder Bot
# Supports both AMD64 (Intel) and ARM64 (Apple Silicon M1/M2/M3)

FROM python:3.13-slim-trixie

# Set build arguments for multi-arch support
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Labels for container metadata
LABEL maintainer="ITSD Team"
LABEL description="Slack Reminder Bot for ITSD HelpDesk"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Pull Debian security fixes published since the base image was cut
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Create data directory for persistent storage
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Install dependencies
COPY requirements.lock.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.lock.txt

# Copy application code
COPY --chown=appuser:appgroup src/ ./src/

# Switch to non-root user
USER appuser

# Health check: the main loop touches the heartbeat at least every 15 min
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os,sys,time; sys.exit(0 if time.time() - os.path.getmtime('/tmp/itsd-reminder.heartbeat') < 1800 else 1)" || exit 1

# Run the application
CMD ["python", "-u", "src/main.py"]
