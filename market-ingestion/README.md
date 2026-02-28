# Market Ingestion Service

A FastAPI-based microservice for market data ingestion.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) — a fast Python package and project manager

### Installing uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS via Homebrew
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, verify it works:

```bash
uv --version
```

## Getting Started

### 1. Install dependencies

From the `market-ingestion/` directory:

```bash
uv sync
```

This creates a `.venv` virtual environment and installs all dependencies from `uv.lock`.

### 2. Run the development server

```bash
uv run python main.py
```

The server starts at http://localhost:8000 with auto-reload enabled.

### 3. Verify it's running

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

API docs are available at http://localhost:8000/docs (Swagger UI).

## Common uv Commands

| Command | Description |
|---|---|
| `uv sync` | Install/sync all dependencies from the lockfile |
| `uv add <package>` | Add a new dependency |
| `uv remove <package>` | Remove a dependency |
| `uv run <command>` | Run a command inside the project's virtual environment |
| `uv lock` | Regenerate the lockfile without installing |
| `uv tree` | Show the dependency tree |

## Project Structure

```
market-ingestion/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI app and routes
├── main.py              # Entrypoint (runs uvicorn)
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock              # Pinned dependency lockfile
└── README.md
```
