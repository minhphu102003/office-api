import base64
import json
import shutil
import uuid
from pathlib import Path
from typing import Any
from office_mcp.core.client import run_officecli

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _resolve_source(source: str) -> Path | None:
    p = Path(source)
    if p.exists():
        return p
    for ext in (".docx", ".xlsx", ".pptx"):
        p = Path(f"{source}{ext}")
        if p.exists():
            return p
    return None


def create_template(
    source: str,
    output_filename: str,
    replacements: dict[str, str],
) -> dict[str, Any]:
    """Create a template by applying find/replace on an existing file. The agent is responsible for analyzing the document and deciding what text should become {{placeholder}} markers. This tool preserves the original formatting.

    Typical workflow:
    1. Agent reads the user's document locally → extracts text
    2. Agent analyzes → creates markdown preview of proposed placeholders
    3. User approves the markdown
    4. Agent calls this tool with the original file path + replacements
    5. This tool mechanically applies find/replace via officecli, preserving all formatting

    Args:
        source: Path to the original file on disk (e.g. 'C:/Users/.../contract.docx' or just 'contract' if it has a standard extension)
        output_filename: Template filename to save (e.g. 'contract_template.docx')
        replacements: Dict mapping original text → placeholder, e.g. {"Acme Corp": "{{company_name}}", "John Doe": "{{client_name}}"}
    """
    ext = Path(output_filename).suffix.lower()
    if ext not in (".docx", ".xlsx", ".pptx"):
        return {"success": False, "error": f"Unsupported format '{ext}'. Must be .docx, .xlsx, or .pptx"}

    source_path = _resolve_source(source)
    if source_path is None:
        return {"success": False, "error": f"Source file '{source}' not found"}

    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = TEMPLATES_DIR / f"__create_template_{uuid.uuid4().hex[:8]}{ext}"

    try:
        shutil.copy2(str(source_path), str(temp_path))

        if replacements:
            commands = [
                {"command": "set", "path": "/", "find": find_text, "replace": replace_text}
                for find_text, replace_text in replacements.items()
                if find_text and replace_text
            ]
            if commands:
                cmds_json = json.dumps(commands)
                batch_result = run_officecli("batch", str(temp_path), cmds_json, timeout=120)
                if isinstance(batch_result, dict) and batch_result.get("error"):
                    return {"success": False, "error": f"Failed to apply replacements: {batch_result['error']}"}

        final_path = TEMPLATES_DIR / output_filename
        if final_path.exists():
            final_path.unlink()
        temp_path.rename(final_path)

        return {
            "success": True,
            "name": Path(output_filename).stem,
            "filename": output_filename,
            "format": ext[1:],
            "size": final_path.stat().st_size,
            "placeholders": list(replacements.values()),
            "replacements_applied": len(replacements),
        }
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return {"success": False, "error": f"Failed to create template: {e}"}


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
