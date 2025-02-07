FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y gcc

# Copy dependency configuration and install dependencies using uv & hatch
COPY pyproject.toml .
RUN pip install --upgrade pip && pip install uv hatch
RUN uv install

# Copy the rest of the application code
COPY . .

# Expose the port and run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 