FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system packages required for building native extensions and common multimedia libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    ca-certificates \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    cargo \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY backend/requirements.txt /app/requirements.txt

# Upgrade pip and install Python deps
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY .

# Expose port (Render will set PORT env; default to 8000)
EXPOSE 8000
ENV PORT=8000

# Start command uses $PORT if provided by the environment
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
