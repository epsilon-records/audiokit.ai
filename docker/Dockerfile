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

# Instead of copying a pre-created requirements.txt, copy pyproject.toml
# and generate requirements.txt using uv.
COPY packages/audiokit_ai/pyproject.toml ./pyproject.toml
RUN pip install --upgrade pip && \
    pip install uv && \
    uv pip compile pyproject.toml --output-file requirements.txt && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .
RUN pip install packages/audiokit_ai  # Install the local package non-editably for production use

# -------- Stage 2: Production --------
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Copy the installed dependencies and application files from the builder stage.
# This step ensures the final image does not include build dependencies.
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Expose the port your FastAPI app will listen on.
EXPOSE 8000

# Start the server using Gunicorn with Uvicorn workers.
CMD ["gunicorn", "audiokit_ai.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]