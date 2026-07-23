from pathlib import Path
from pydantic import AnyUrl
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import TextResource
from office_mcp.core.skill_loader import load_skills, SKILLS_DIR
from office_mcp.tools.templates import list_templates, upload_template
from office_mcp.tools.documents import create_doc, view_template
from office_mcp.tools.drafts import create_draft, update_draft, get_draft, list_drafts, delete_draft, generate_from_draft
from office_mcp.tools.info import get_doc_info, download_doc

INSTRUCTIONS = """# Office-MCP: Template Document Generator

Generate documents (.docx, .xlsx, .pptx) from pre-existing templates by merging JSON data into {{placeholder}} markers.

## Stateful Workflow (recommended)
Use drafts to accumulate data incrementally — the workflow is resumable if interrupted:

1. `list_templates` → see available templates
2. `view_template` → inspect placeholders
3. `create_draft(template)` → start a draft, get a draft_id
4. `update_draft(draft_id, data)` → fill in placeholders gradually (call multiple times)
5. `generate_from_draft(draft_id, output_filename)` → produce the final doc
6. `download_doc(output_filename)` → retrieve the file as base64, save to user's machine

Use `list_drafts()` to see in-progress drafts, `get_draft(draft_id)` to check accumulated data.

## Stateless Workflow (simple)
1. `list_templates` → see available templates
2. `view_template` → inspect placeholders
3. `create_doc` → merge data into template and produce output
4. `download_doc` → retrieve the file

## When to use
- User asks to create invoices, contracts, reports, letters from a template
- User provides partial data — use `create_draft` + `update_draft` to collect it gradually
- User wants a formatted document with all data ready — use `create_doc` directly

## Formatting Standards
Before creating documents, read the relevant formatting guide:
- `skill://format/word-format` — Word (.docx) font, spacing, margins, heading hierarchy
- `skill://format/excel-format` — Excel (.xlsx) tables, alignment, number formats, colors
- `skill://format/powerpoint-format` — PowerPoint (.pptx) layouts, typography, slide rules

Apply these standards when creating templates or filling placeholders.

## When NOT to use
- User wants a fully custom document from scratch — use the REST API endpoints instead
"""

mcp = FastMCP("office-mcp", instructions=INSTRUCTIONS)

mcp.add_tool(list_templates)
mcp.add_tool(upload_template)
mcp.add_tool(create_doc)
mcp.add_tool(view_template)
mcp.add_tool(get_doc_info)
mcp.add_tool(download_doc)
mcp.add_tool(create_draft)
mcp.add_tool(update_draft)
mcp.add_tool(get_draft)
mcp.add_tool(list_drafts)
mcp.add_tool(delete_draft)
mcp.add_tool(generate_from_draft)

# ── Main server skill ──
SKILL_PATH = Path(__file__).parent / "SKILL.md"
if SKILL_PATH.exists():
    skill_content = SKILL_PATH.read_text()
    mcp.add_resource(TextResource(
        uri=AnyUrl("skill://guide"),
        name="MCP Server Guide",
        description="Full usage guide for office-mcp server, including workflows and examples",
        mime_type="text/markdown",
        text=skill_content,
    ))

# ── Formatting skills (loaded from skills/<name>/SKILL.md) ──
for skill in load_skills():
    mcp.add_resource(TextResource(
        uri=AnyUrl(f"skill://format/{skill['name']}"),
        name=f"{skill['name']} Formatting Standards",
        description=skill["description"],
        mime_type="text/markdown",
        text=skill["text"],
    ))

app = mcp.sse_app()
