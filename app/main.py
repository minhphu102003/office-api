import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.documents import router as documents_router
try:
    from office_mcp.server import app as mcp_app
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    binary = Path(settings.officecli_path)
    if not binary.exists():
        print(f"WARNING: OfficeCLI binary not found at {binary.resolve()}", file=sys.stderr)
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="OfficeCLI API",
    description="FastAPI backend service for OfficeCLI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)

if HAS_MCP:
    app.mount("/mcp", mcp_app, name="mcp")
    print("MCP server mounted at /mcp", file=sys.stderr)
