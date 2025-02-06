AudioKit Project Setup
=====================

Prerequisites
------------
- Python 3.11+
- Poetry
- Ruff (for formatting and linting)

Project Structure
----------------
├── audiokit/                    # Client package
│   ├── audiokit/
│   │   ├── __init__.py         # AudioKit client class
│   │   ├── cli.py              # Typer-based CLI
│   │   └── plugin.py           # Plugin system
│   ├── tests/
│   │   ├── test_client.py      # Client tests
│   │   ├── test_cli.py         # CLI tests
│   │   └── test_plugin.py      # Plugin tests
│   ├── pyproject.toml          # Poetry & tool config
│   └── README.md               # Package docs
│
└── audiokit-ai/                # Backend service
    ├── audiokit_ai/
    │   ├── __init__.py
    │   ├── main.py             # FastAPI app
    │   ├── processing.py       # Audio processing
    │   └── models.py           # Pydantic models
    ├── tests/
    │   ├── test_api.py         # API tests
    │   └── test_processing.py  # Processing tests
    ├── pyproject.toml          # Poetry & tool config
    └── README.md               # Service docs

Initial Setup
------------
1. Client Package:
```bash
cd audiokit
poetry install
poetry run ruff format .
poetry run ruff check .
poetry run pytest
```

2. Backend Service:
```bash
cd audiokit-ai
poetry install
poetry run ruff format .
poetry run ruff check .
poetry run pytest
```

Development Workflow
------------------
1. Format and lint code:
```bash
poetry run ruff format .
poetry run ruff check .
```

2. Run tests:
```bash
poetry run pytest --cov
```

3. Start backend service:
```bash
poetry run uvicorn audiokit_ai.main:app --reload
```

4. Use CLI:
```bash
poetry run audiokit analyze input.wav
poetry run audiokit process input.wav -o output.wav
poetry run audiokit generate params.json -o output.wav
```

Configuration
------------
1. Environment Variables:
```bash
export AUDIOKIT_AI_URL=http://localhost:8000
export AUDIOKIT_API_KEY=your-api-key
```

2. Poetry Dependencies:
```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name
```

Documentation
------------
1. Generate API docs:
```bash
poetry run pdoc --html audiokit
```

2. View OpenAPI docs:
- http://localhost:8000/docs
- http://localhost:8000/redoc