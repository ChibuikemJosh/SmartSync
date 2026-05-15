# Use the exact version to match your .python-version
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# 1. Install system dependencies
# Added libmagic for file type detection and cleaned up apt to keep image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    libsndfile1 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 2. Setup Python environment
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 3. Leverage Docker caching for dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application
# FIX: Use '.' to copy current dir to WORKDIR
COPY . .

# 5. Security: Run as non-root user
# This prevents the app from having admin rights inside the container
RUN useradd -m smartsync
USER smartsync

# 6. Expose and Run
EXPOSE 8000

# We use the shell form to allow variable substitution for PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}