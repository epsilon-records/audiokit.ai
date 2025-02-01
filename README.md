# Epsilon Music Platform

A modern music distribution and artist management platform built with SvelteKit 2 and Python.

## Project Structure

```
epsilon/
├── apps/
│   └── web/               # SvelteKit 2 frontend
├── packages/
│   └── audiokit/          # Python backend services
├── justfile              # Command runner
└── README.md
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

## Code Quality

- Python code is formatted and linted with [ruff](https://github.com/astral-sh/ruff)
- TypeScript/Svelte code is formatted with Prettier and linted with ESLint
- All code changes should pass `just check` before committing

## Documentation

- Backend API documentation is generated with `just audiokit-docs`
- Frontend documentation is available in the `apps/web/README.md`

## License

MIT
