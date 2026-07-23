import base64
import os
from pathlib import Path
from typing import Any
from office_mcp.core.client import run_officecli

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(Path(__file__).parent.parent / "output")))


def get_doc_info(filepath: str) -> dict[str, Any]:
    """Get structured info (stats, outline) about a generated document in the output directory. Useful after create_doc to verify the output.

    Args:
        filepath: Filename in the output directory (e.g. 'invoice_acme.docx')
    """
    full_path = OUTPUT_DIR / filepath
    if not full_path.exists():
        return {"success": False, "error": f"File '{filepath}' not found in output directory"}

    stats = run_officecli("view", str(full_path), "stats", timeout=15)
    outline = run_officecli("view", str(full_path), "outline", timeout=15)
    return {
        "success": True,
        "path": str(full_path),
        "stats": stats.get("data", {}),
        "outline": outline.get("data", {}),
    }


def download_doc(filepath: str) -> dict[str, Any]:
    """Download a generated document as base64-encoded content. The agent can use this to save the file to the user's local machine.

    Args:
        filepath: Filename in the output directory (e.g. 'invoice_acme.docx')
    """
    full_path = OUTPUT_DIR / filepath
    if not full_path.exists():
        return {"success": False, "error": f"File '{filepath}' not found in output directory"}

    content_bytes = full_path.read_bytes()
    return {
        "success": True,
        "filename": filepath,
        "format": full_path.suffix[1:],
        "size": full_path.stat().st_size,
        "content_base64": base64.b64encode(content_bytes).decode(),
    }
