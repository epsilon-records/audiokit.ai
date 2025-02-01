# List all available commands
default:
    @just --list

# Install all dependencies (both Python and Node.js)
install:
    cd packages/audiokit && poetry install
    cd apps/web && bun install

# Install dependencies for audiokit package
audiokit-install:
    cd packages/audiokit && poetry install

# Run audiokit pipeline for a specific artist
audiokit-run artist_id:
    cd packages/audiokit && poetry run python -c "from audiokit.core import run_audiokit_ai_pipeline; import asyncio; asyncio.run(run_audiokit_ai_pipeline('{{artist_id}}'))"

# Run audiokit tests
audiokit-test:
    cd packages/audiokit && poetry run pytest

# Clean audiokit cache files
audiokit-clean:
    find packages/audiokit -type f -name "*.pyc" -delete
    find packages/audiokit -type d -name "__pycache__" -delete
    find packages/audiokit -type d -name "*.egg-info" -exec rm -r {} +
    cd packages/audiokit && poetry env remove --all

# Format all code
format:
    cd packages/audiokit && poetry run ruff format .
    cd apps/web && bun run format

# Format audiokit code
audiokit-format:
    cd packages/audiokit && poetry run ruff format .

# Check all code
check:
    cd packages/audiokit && poetry run ruff check .
    cd apps/web && bun run lint

# Fix all auto-fixable issues
fix:
    cd packages/audiokit && poetry run ruff check --fix .
    cd apps/web && bun run lint --fix

# Run development environment
dev:
    #!/usr/bin/env bash
    trap 'kill 0' SIGINT
    cd packages/audiokit && poetry run uvicorn audiokit.server:app --reload --port 8000 &
    cd apps/web && bun run dev

# Run audiokit development server
audiokit-dev:
    cd packages/audiokit && poetry run uvicorn audiokit.server:app --reload --port 8000

# Generate audiokit documentation
audiokit-docs:
    cd packages/audiokit && poetry run pdoc --html --output-dir docs audiokit

# Show audiokit package version
audiokit-version:
    cd packages/audiokit && poetry run python -c "from audiokit import __version__; print(__version__)"

# Build for production
build:
    cd packages/audiokit && poetry build
    cd apps/web && bun run build

# Clean all dependencies and build artifacts
clean: audiokit-clean
    cd apps/web && rm -rf node_modules .svelte-kit build
    rm -rf .venv node_modules

# Update all dependencies
update:
    cd packages/audiokit && poetry update
    cd apps/web && bun update

# Run the audiokit core module
run-audiokit:
    cd packages/audiokit && poetry run python -m audiokit.core