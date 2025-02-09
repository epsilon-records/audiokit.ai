# Use a minimal base image
FROM python:3.10-slim-bullseye AS builder

# Use a dedicated directory for better organization
WORKDIR /app

# Install required build dependencies (cached layer)
RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    apt-get update && apt-get install -y --no-install-recommends \
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

# Install a virtual environment to isolate dependencies
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Copy dependency files first (for layer caching)
COPY pyproject.toml .

# Upgrade pip and install dependencies efficiently with cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv pip compile pyproject.toml -o requirements.txt

# Install dependencies efficiently (cached layer)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --prefer-binary -r requirements.txt llvmlite==0.44.0

# Copy only the necessary source files (avoid large .git, .pytest_cache, etc.)
COPY . .

# Install the application inside the virtual environment
RUN pip install --no-cache-dir -e .

# Final runtime image
FROM python:3.10-slim-bullseye AS runtime

# Set up non-root user (security best practice)
RUN useradd --create-home appuser

# Set working directory
WORKDIR /app

# Copy only necessary components from the builder stage
COPY --from=builder /venv /venv
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/venv/bin:$PATH"

# Remove unnecessary files to shrink image size
RUN rm -rf /root/.cache /usr/local/share/.cache /tmp/*

# Expose port
EXPOSE 8000

# Start the application with optimized worker settings
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
