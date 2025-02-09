# Use a minimal base image
FROM python:3.10-slim-bullseye

# Set up non-root user (security best practice)
RUN useradd --create-home appuser

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

# Install dependencies efficiently with cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip

# Install each package individually with a cache mount for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary numpy

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary "torch>=1.13.0"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary "torchaudio>=0.13.0"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary faiss-cpu

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary openai-whisper

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary "deepfilternet>=0.5.6"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary "deepfilterlib>=0.5.6"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary google-cloud-speech

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary "tensorflow>=2.18.0"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary pandas==2.2.3

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary scikit-learn==1.6.1

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary scikit-image==0.25.1

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary moviepy==2.1.2

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary librosa==0.10.2.post1

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary statsmodels==0.14.4

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary redis

# Copy dependency files first (for layer caching)
COPY pyproject.toml .

# Install core dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary .

# Install test dependencies separately
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary .[test]

# Copy application files after dependencies
COPY . .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Expose port
EXPOSE 8000

# Switch to appuser
USER appuser

# Start the application with optimized worker settings
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
