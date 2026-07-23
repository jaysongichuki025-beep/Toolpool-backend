# ═══════════════════════════════════════════════════════════════════════════
# Dockerfile — Build instructions for the Django backend container
# ═══════════════════════════════════════════════════════════════════════════
# WHY Docker?
#   Packages the app + Python + system libraries into one portable image.
#   Same image runs on your laptop, Render, or any cloud host.
#
# Build:  docker compose build
# Run:    docker compose up
# ═══════════════════════════════════════════════════════════════════════════

# Base image = official Python 3.12 on a small Linux (slim = fewer packages)
FROM python:3.12-slim

# Prevent Python from writing .pyc files and from buffering stdout
# WHY: logs appear immediately in docker logs (easier debugging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Install system packages needed to compile psycopg2 (Postgres driver)
# apt-get = Debian package manager inside the slim image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching — rebuilds faster when only code changes)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project into the image
COPY . .

# Document that the container listens on port 8000
EXPOSE 8000

# Default command: migrate DB then start gunicorn (production server)
# In docker-compose.dev we override this with runserver for hot-reload
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
