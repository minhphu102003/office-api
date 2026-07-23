# OfficeCLI API

FastAPI backend + MCP server wrapping OfficeCLI to generate .docx, .xlsx, .pptx from templates.

## Quick Start (Docker)

```bash
# 1. Clone & enter
git clone <repo> && cd office-api

# 2. Copy env and set your API key
cp .env.example .env
# Edit .env → OPENAI_API_KEY=sk-...

# 3. Start
docker compose up -d
```

The service is now at `http://localhost:8000`.

## Integrations

### opencode.ai

Add to `opencode.json` in your project root:

```json
{
  "mcp": {
    "office-mcp": {
      "type": "remote",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

### Grok

```bash
grok mcp add --transport http office-mcp http://localhost:8000/mcp/
```

### Visual Studio Code

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "office-mcp": {
      "type": "sse",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

Or add globally in VS Code settings (`mcp.servers`).

### Claude Desktop

Create/edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "office-mcp": {
      "type": "sse",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

**Windows path:** `%APPDATA%\Claude\claude_desktop_config.json`

### Codex CLI

Create `.codex/config.json`:

```json
{
  "mcpServers": {
    "office-mcp": {
      "type": "sse",
      "url": "http://localhost:8000/mcp/"
    }
  }
}
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `list_templates` | List available document templates |
| `view_template` | Inspect {{placeholders}} in a template |
| `create_doc` | Generate doc by merging JSON into template |
| `create_draft` | Start a draft for incremental data entry |
| `update_draft` | Append data to an existing draft |
| `generate_from_draft` | Finalize draft into a document |
| `get_draft` | Read draft state and accumulated data |
| `list_drafts` | List all drafts (filter by status) |
| `delete_draft` | Remove a draft |
| `download_doc` | Download a generated file as base64 |
| `upload_template` | Upload a new .docx/.xlsx/.pptx template |
| `get_doc_info` | Get stats and outline of a document |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | LLM provider API key |
| `LLM_BASE_URL` | `https://api.openai.com/v1` | LLM endpoint |
| `LLM_MODEL` | `gpt-4o` | Model name |
| `OUTPUT_DIR` | `output` | Where generated files go |
| `OFFICECLI_PATH` | `bin/officecli` | Path to OfficeCLI binary |

## API Endpoints

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: `GET /health`

## Local Development

```bash
# Create venv
uv venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install
uv pip install -e .

# Download OfficeCLI into bin/
# https://github.com/iOfficeAI/OfficeCLI/releases

# Run
uvicorn app.main:app --reload --port 8000
```

## CLI (stdio)

Run the MCP server locally without HTTP:

```bash
office-mcp
```
