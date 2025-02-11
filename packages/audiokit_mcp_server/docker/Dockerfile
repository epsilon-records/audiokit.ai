# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and add to PATH
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy entire package context
COPY . .

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies (only main/production)
RUN poetry install --only main --no-interaction --no-ansi

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run uvicorn directly
CMD ["uvicorn", "audiokit_mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"] 