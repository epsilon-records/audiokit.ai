# Build stage
FROM python:3.10-slim-bullseye AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    build-essential \
    cmake \
    && wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && echo "deb http://apt.llvm.org/bullseye/ llvm-toolchain-bullseye-11 main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    llvm-11-dev \
    clang-11 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv and generate requirements
COPY pyproject.toml .
RUN pip install --no-cache-dir uv \
    && uv pip compile pyproject.toml -o requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt llvmlite==0.44.0

# Copy application code
COPY . .

# Install in editable mode
RUN pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.10-slim-bullseye

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

WORKDIR /app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]