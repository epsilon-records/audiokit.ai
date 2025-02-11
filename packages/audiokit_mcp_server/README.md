# AudioKit MCP Server

FastAPI server providing music analytics through Soundcharts API integration with RAG-powered insights using Weaviate and Claude-3.5-Sonnet.

## Features

- **Music Analytics**: Real-time artist and song analytics via Soundcharts API
- **Intelligent Insights**: RAG system using Weaviate and Claude-3.5-Sonnet
- **Historical Analysis**: Track trends and performance over time
- **Platform Coverage**: Data from Spotify, Apple Music, YouTube, TikTok, and more

## Installation

### Prerequisites

- Python 3.9+
- Poetry (recommended) or pip
- Weaviate instance
- API keys for:
  - OpenRouter
  - Soundcharts
  - Weaviate

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Copy and configure environment variables
cp .env.example .env
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
```

## Configuration

Required environment variables:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Soundcharts API Configuration
SOUNDCHARTS_APP_ID=your_app_id
SOUNDCHARTS_API_KEY=your_api_key

# Weaviate Configuration
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_key
```

## Usage

### Start the Server

Using Poetry:

```bash
poetry run uvicorn main:app --reload
```

Using Python directly:

```bash
python main.py
```

### API Endpoints

#### Analyze Artist

```bash
curl -X POST http://localhost:8000/analyze/spotify \
  -H "Content-Type: application/json" \
  -d '{
    "spotify_uri": "spotify:artist:6eUKZXaKkcviH0Ku9w2n3V",
    "query": "What are the key trends for this artist?"
  }'
```

## Development

### Code Style

```bash
# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy .

# Linting
poetry run flake8
```

### Testing

```bash
poetry run pytest
```

## Project Structure

```text
audiokit_mcp_server/
├── handlers/
│   ├── analytics_rag.py      # Analytics and RAG system
│   ├── soundcharts_client.py # Soundcharts API client
├── main.py                   # FastAPI application
├── pyproject.toml           # Poetry configuration
├── requirements.txt         # pip requirements
└── .env.example            # Environment template
```

## API Documentation

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
