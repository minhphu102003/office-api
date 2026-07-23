from pathlib import Path
from typing import Any
from office_mcp.core.client import run_officecli

OUTPUT_DIR = Path(__file__).parent.parent / "output"


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
