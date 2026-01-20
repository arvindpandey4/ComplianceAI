# Use official lightweight Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image size small
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories for creating data at runtime if needed
RUN mkdir -p /app/data/uploads && \
    mkdir -p /app/data/faiss_index

# Copy the rest of the application code
COPY . .

# Expose the API port
EXPOSE 8000

# Start command
# Using shell form to support $PORT variable expansion
# Render sets PORT env var (default 10000), fallback to 8000 if missing
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
