import json
from typing import Any

from office_mcp.core import store as draft_store
from office_mcp.core.client import run_officecli
from office_mcp.tools.documents import OUTPUT_DIR, _resolve_template


def create_draft(template: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Start a new document draft. Saves placeholder data incrementally so the workflow can be resumed later. Call view_template first to see what placeholders are available.

    Args:
        template: Template name or filename (e.g. 'invoice_template' or 'invoice_template.docx')
        data: Optional initial data to pre-fill placeholders
    """
    template_path = _resolve_template(template)
    if template_path is None:
        return {"success": False, "error": f"Template '{template}' not found"}
    result = draft_store.create_draft(template_path.stem, data)
    if result["success"]:
        result["template_name"] = template_path.stem
    return result


def update_draft(draft_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Merge new data into an existing draft. Existing keys are overwritten, new keys are added.

    Args:
        draft_id: Draft ID returned by create_draft
        data: Key-value pairs to merge into the draft
    """
    return draft_store.update_draft(draft_id, data)


def get_draft(draft_id: str) -> dict[str, Any]:
    """Get the current state of a draft including all accumulated data.

    Args:
        draft_id: Draft ID returned by create_draft
    """
    return draft_store.get_draft(draft_id)


def list_drafts(status: str | None = None) -> dict[str, Any]:
    """List all document drafts, optionally filtered by status (draft, completed).

    Args:
        status: Filter by status ('draft' or 'completed'). If omitted, returns all drafts.
    """
    return draft_store.list_drafts(status)


def delete_draft(draft_id: str) -> dict[str, Any]:
    """Delete a draft and its accumulated data.

    Args:
        draft_id: Draft ID returned by create_draft
    """
    return draft_store.delete_draft(draft_id)


def generate_from_draft(draft_id: str, output_filename: str) -> dict[str, Any]:
    """Generate the final document from a completed draft. Merges all accumulated data into the template and saves the output file. Use download_doc to retrieve the file content.

    Args:
        draft_id: Draft ID returned by create_draft
        output_filename: Name for the generated file (e.g. 'invoice_acme.docx')
    """
    draft = draft_store.get_draft(draft_id)
    if not draft["success"]:
        return draft
    if not draft["data"]:
        return {"success": False, "error": "Draft has no data to merge"}

    template_path = _resolve_template(draft["template_name"])
    if template_path is None:
        return {"success": False, "error": f"Template '{draft['template_name']}' not found"}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename
    result = run_officecli("merge", str(template_path), str(output_path), "--data", json.dumps(draft["data"]), timeout=60)

    draft_store.set_draft_status(draft_id, "completed", output_filename)
    return {
        "success": result.get("success", True),
        "filename": output_filename,
        "format": output_path.suffix[1:],
        "template": draft["template_name"],
        "draft_id": draft_id,
    }
