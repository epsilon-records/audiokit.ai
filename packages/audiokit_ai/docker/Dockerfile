# Use an official Python image as a base.
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files and to buffer stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install OS-level dependencies.
# - build-essential for compiling C extensions
# - git is sometimes needed to fetch dependencies
# - libsndfile1 is required for torchaudio (and possibly other audio libraries)
# - libopenblas-dev & libomp-dev support faiss-cpu (if a wheel isn't available)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libsndfile1 \
    libopenblas-dev \
    libomp-dev \
 && rm -rf /var/lib/apt/lists/*

# Set work directory.
WORKDIR /app

# Copy the project code into the container.
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Hatchling (required for building using your pyproject.toml)
RUN pip install hatchling

# Install your project (non-editably) along with test extras.
RUN pip install '.[test]'

# Expose the port if you plan to run your FastAPI app (adjust port as needed).
EXPOSE 8000

# Default command can be to run tests; you can also override this, for example using uvicorn to start your server.
# For tests:
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
# If you want to run the app (uncomment next line and comment the CMD above)
# CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"] 