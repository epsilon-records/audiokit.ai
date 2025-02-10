# Use NVIDIA base image
FROM nvidia/cuda:12.2.0-base-ubuntu22.04

# Set non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies (BEFORE installing pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    python3.10 \
    python3-pip \
    python3.10-venv \
    ffmpeg \
    libsndfile1 \
    wget \
    gnupg \
    build-essential \
    cmake \
    git \
    llvm-11-dev \
    clang-11 \
    python3-numpy \
    python3-sklearn \
    python3-scipy \
    python3-statsmodels \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure CUDA/cuDNN paths
ENV LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH
ENV XLA_FLAGS="--xla_gpu_cuda_data_dir=/usr/local/cuda-12.2"
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV CUDA_VISIBLE_DEVICES=0

# Set up non-root user (security best practice)
RUN useradd --create-home appuser

# Use a dedicated directory for better organization
WORKDIR /app

# Upgrade pip before installing dependencies
RUN pip install --upgrade pip

# Install Python dependencies (ONE TIME, no duplication)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary \
        torch==2.6.0 \
        torchaudio==2.6.0 \
        tensorflow[and-cuda]==2.18.0 \
        nvidia-cudnn-cu12==8.9.4 \
        demucs==4.0.1 \
        deepfilternet==0.5.6 \
        openai-whisper==v20240930 \
        faiss-cpu==1.8.0 \
        pandas==2.2.3 \
        scikit-image==0.25.1 \
        moviepy==2.1.2 \
        librosa==0.10.2.post1 \
        google-cloud-speech==2.20.0

# Set environment variables for CUDA
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV XLA_PYTHON_CLIENT_ALLOCATOR=platform
ENV TF_FORCE_GPU_ALLOW_GROWTH=true

# Copy project configuration before installing core dependencies
COPY pyproject.toml .

# Install project dependencies (ONLY ONCE)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary .

# Install test dependencies separately
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefer-binary .[test]

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Expose port
EXPOSE 8000

# Switch to appuser
USER appuser

# Create cache directory and set permissions
RUN mkdir -p /home/appuser/.cache/DeepFilterNet && \
    chown -R appuser:appuser /home/appuser/.cache

# Start the application with optimized worker settings
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]