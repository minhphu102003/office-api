import base64
from pathlib import Path
from typing import Any
from office_mcp.core.client import run_officecli

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def list_templates() -> list[dict[str, Any]]:
    """List all available document templates. Call this first to see what templates exist and their formats (docx/xlsx/pptx). Each template contains {{placeholder}} markers that can be filled with data via create_doc."""
    if not TEMPLATES_DIR.exists():
        return []
    templates = []
    for f in sorted(TEMPLATES_DIR.glob("*")):
        if f.suffix.lower() in (".docx", ".xlsx", ".pptx"):
            info = run_officecli("view", str(f), "stats", timeout=15)
            templates.append({
                "name": f.stem,
                "filename": f.name,
                "format": f.suffix[1:],
                "size": f.stat().st_size,
                "info": info.get("data", {}),
            })
    return templates


def upload_template(filename: str, content: str) -> dict[str, Any]:
    """Upload a template file (base64-encoded) to the templates directory.

    Args:
        filename: Template filename with extension (e.g. 'invoice_template.docx')
        content: Base64-encoded file content
    """
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    filepath = TEMPLATES_DIR / filename
    try:
        decoded = base64.b64decode(content)
        filepath.write_bytes(decoded)
        return {"success": True, "path": str(filepath), "size": len(decoded)}
    except Exception as e:
        return {"success": False, "error": f"Upload failed: {e}"}
