# AudioKit Music Platform

A modern music distribution and artist management platform built with SvelteKit 2 and Python.

## Project Structure

```
audiokit/
  apps/
    web/                  # Svelte frontend application
      src/               
      package.json
      tsconfig.json
      vite.config.ts
      tailwind.config.ts
  
  packages/
    audiokit/            # Python backend package
      audiokit/
        core.py         # Core audio processing
        db.py          # Database operations
        llm.py         # AI/ML functionality
        logger.py      # Logging utilities
        utils.py       # Helper functions
      tests/
      pyproject.toml
      poetry.lock
      README.md

  .cursorrules          # Development guidelines
  .env                  # Environment configuration
  justfile             # Command runner
  README.md            # Project documentation
```

## Prerequisites

- [Poetry](https://python-poetry.org/) for Python dependency management
- [Bun](https://bun.sh/) for Node.js dependency management
- [Just](https://github.com/casey/just) command runner

## Getting Started

1. Install dependencies:

```bash
just install
```

2. Start development servers:

```bash
just dev
```

The web app will be available at `http://localhost:5173` and the API at `http://localhost:8000`.

## Available Commands

### Development

- `just dev` - Start both frontend and backend development servers
- `just audiokit-dev` - Start only the backend server
- `just format` - Format all code with ruff and Prettier
- `just check` - Check code for issues
- `just fix` - Auto-fix code issues where possible

### Building

- `just build` - Build both packages for production
- `just audiokit-install` - Install only backend dependencies
- `just clean` - Clean all build artifacts and dependencies
- `just update` - Update all dependencies

### Testing

- `just audiokit-test` - Run backend tests
- `just audiokit-docs` - Generate backend API documentation

### Utilities

- `just audiokit-version` - Show backend package version
- `just audiokit-run <artist_id>` - Run AI pipeline for a specific artist

## Core Technical Stack

### Frontend Framework (apps/web)

- Svelte 5 with Runes
- SvelteKit 2 for routing and server features
- TypeScript for all code
- Tailwind CSS with Shadcn UI components
- Paraglide.js for internationalization
- Vite for build tooling

### Backend Services (packages/audiokit)

- Python 3.11+ with Poetry
- FastAPI for API endpoints
- SQLAlchemy 2.0 for database operations
- Celery for background job processing
- Redis for caching and message queue
- Docker for containerization

## Code Quality

- Python code is formatted and linted with [ruff](https://github.com/astral-sh/ruff)
- TypeScript/Svelte code is formatted with Prettier and linted with ESLint
- All code changes should pass `just check` before committing

## Documentation

- Backend API documentation is generated with `just audiokit-docs`
- Frontend documentation is available in the `apps/web/README.md`
- OpenAPI specification for API endpoints
- Component storybook for UI components

## License

MIT
