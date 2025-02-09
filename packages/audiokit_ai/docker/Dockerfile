# Use a more complete base image that includes LLVM repositories
FROM python:3.10-bullseye

# Add LLVM repository and install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add - \
    && echo "deb http://apt.llvm.org/bullseye/ llvm-toolchain-bullseye-11 main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y \
    build-essential \
    cmake \
    llvm-11-dev \
    clang-11 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv temporarily to generate requirements.txt
RUN pip install uv

# Copy pyproject.toml and generate requirements.txt
COPY pyproject.toml .
RUN uv pip compile pyproject.toml -o requirements.txt && \
    pip install --use-pep517 llvmlite llvmlite==0.44.0

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install the package in editable mode
RUN pip install -e .

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]