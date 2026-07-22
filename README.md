# OfficeCLI API

FastAPI backend service wrapping OfficeCLI with LLM integration.

## Setup

```bash
# Create virtual environment
uv venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Copy .env.example to .env and fill in your keys
```

## Download OfficeCLI

Download `officecli-win-x64.exe` from [GitHub Releases](https://github.com/iOfficeAI/OfficeCLI/releases) and place it in `bin/officecli.exe`.

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Create document
curl -X POST http://localhost:8000/api/v1/documents/create \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.pptx", "format": "pptx"}'
```
