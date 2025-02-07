# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install hatchling && \
    pip install '.[test]'

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    libopenblas-dev \
    libomp-dev \
 && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"] 