# Use a smaller base image
FROM python:3.10-slim-bullseye AS builder

# Install required build dependencies
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

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml .
RUN pip install --no-cache-dir uv \
    && uv pip compile pyproject.toml -o requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt llvmlite==0.44.0

# Copy only necessary application files
COPY . .

# Install the application
RUN pip install --no-cache-dir -e .

# -- Final runtime image --
FROM python:3.10-slim-bullseye

# Set working directory
WORKDIR /app

# Copy only the required parts from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

# Remove unnecessary files to shrink image size
RUN rm -rf /root/.cache /usr/local/share/.cache /tmp/*

# Set a non-root user for better security (optional)
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Use a more efficient startup command
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]