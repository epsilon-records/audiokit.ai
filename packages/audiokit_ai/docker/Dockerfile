# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency descriptor so that pip install layers are cached
COPY pyproject.toml ./pyproject.toml

# Upgrade pip, install uv, compile requirements and install them
RUN pip install --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip compile pyproject.toml --output-file requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (this layer will be rebuilt only when the code changes)
COPY .. .

# Install the local package (if code inside packages/audiokit_ai has changed, this layer will update)
RUN pip install --no-cache-dir .

# -------- Stage 2: Production --------
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Install runtime dependency for torch/torchaudio
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy only the necessary files from builder; this does not include the build dependencies
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Expose the port your FastAPI app will listen on.
EXPOSE 8000

# Start the server using Gunicorn with Uvicorn workers.
CMD ["gunicorn", "audiokit_ai.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]