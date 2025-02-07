FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install dependencies directly (using uv for running uvicorn)
RUN pip install --no-cache-dir uvicorn fastapi celery redis sqlalchemy boto3 pyjwt grpcio grpcio-tools fastapi-limiter

EXPOSE 8000
CMD ["uvicorn", "audiokit_ai.main:app", "--host", "0.0.0.0", "--port", "8000"] 