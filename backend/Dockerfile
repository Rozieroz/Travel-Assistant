# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for sentence-transformers and ChromaDB
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install pinned dependencies that work together
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==1.5.3 \
    chromadb==0.4.22 \
    sentence-transformers==2.2.2 \
    huggingface-hub==0.19.4 \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    python-dotenv==1.0.0 \
    openai==1.3.0 \
    requests==2.31.0

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]