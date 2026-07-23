import json
from pathlib import Path
from typing import Any
from office_mcp.core.client import run_officecli

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def _resolve_template(template: str) -> Path | None:
    p = TEMPLATES_DIR / template
    if p.exists():
        return p
    for ext in (".docx", ".xlsx", ".pptx"):
        p = TEMPLATES_DIR / f"{template}{ext}"
        if p.exists():
            return p
    return None


def create_doc(template: str, data: dict[str, Any], output_filename: str) -> dict[str, Any]:
    """Generate a document by merging JSON data into a template. Replaces all {{placeholder}} markers in the template with the provided data values. Call view_template first to see what placeholders are available.

    Args:
        template: Template name or filename (e.g. 'invoice_template.docx' or just 'invoice_template')
        data: JSON object mapping placeholder names to values (e.g. {"client_name": "Acme", "total": "$5,200"})
        output_filename: Name for the generated file (e.g. 'invoice_acme.docx')
    """
    template_path = _resolve_template(template)
    if template_path is None:
        return {"success": False, "error": f"Template '{template}' not found"}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    result = run_officecli("merge", str(template_path), str(output_path), "--data", json.dumps(data), timeout=60)
    return {
        "success": result.get("success", True),
        "path": str(output_path),
        "template": template,
    }


def view_template(template: str) -> dict[str, Any]:
    """Inspect a template's structure, text content and {{placeholder}} markers. Call this before create_doc to know what data keys to provide.

    Args:
        template: Template name or filename (e.g. 'invoice.docx' or 'invoice_template')
    """
    template_path = _resolve_template(template)
    if template_path is None:
        return {"success": False, "error": f"Template '{template}' not found"}
    text = run_officecli("view", str(template_path), "text", timeout=15)
    outline = run_officecli("view", str(template_path), "outline", timeout=15)
    return {
        "success": True,
        "path": str(template_path),
        "content": text.get("data", {}),
        "outline": outline.get("data", {}),
    }
