import sys
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
Before creating documents, use `read_mcp_resource` with the URI to read the formatting guide. These are static resources — you can read them directly by URI without listing first.
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

# ── Debug: instructions sent? ──
_INSTRUCTIONS_SENT: bool = False

_original_send: object = None


def _wrap_asgi_send(scope, receive, send):
    """Wrap the ASGI send call to detect InitializeResult in responses."""

    _body_buffer: list[bytes] = []

    async def _logged_send(message):
        global _INSTRUCTIONS_SENT
        if message.get("type") == "http.response.body":
            body = message.get("body", b"")
            if body:
                _body_buffer.append(body)
            if not message.get("more_body", False):
                import json
                full = b"".join(_body_buffer).decode()
                _body_buffer.clear()
                # SSE format: event: message\ndata: {...}\n\n
                # Extract JSON from each "data:" line
                for line in full.split("\n"):
                    line = line.strip()
                    if line.startswith("data: ") or line.startswith("data:"):
                        json_text = line[5:].strip()
                        if json_text:
                            try:
                                data = json.loads(json_text)
                                if isinstance(data, dict) and "result" in data:
                                    inst = data["result"].get("instructions")
                                    if inst is not None:
                                        _INSTRUCTIONS_SENT = True
                                        print(
                                            f"[MCP-DEBUG] ✅ InitializeResult SENT with instructions"
                                            f" (len={len(inst)}, preview={inst[:80]!r})",
                                            file=sys.stderr,
                                        )
                                        break
                                    else:
                                        keys = list(data["result"].keys())
                                        if "protocolVersion" in keys:
                                            print(f"[MCP-DEBUG] ⚠️ InitializeResult WITHOUT instructions! keys={keys}", file=sys.stderr)
                                            break
                            except json.JSONDecodeError:
                                pass
        await send(message)

    return _logged_send


async def _debug_asgi_app(scope, receive, send):
    if scope["type"] == "http":
        wrapped_send = _wrap_asgi_send(scope, receive, send)
        await _inner_app(scope, receive, wrapped_send)
    else:
        await _inner_app(scope, receive, send)


# ── Streamable HTTP (cho Grok, opencode,...) ──
mcp.settings.streamable_http_path = "/"
print(
    f"[MCP-DEBUG] FastMCP instructions field: {mcp._mcp_server.instructions is not None}"
    f" (len={len(mcp._mcp_server.instructions or '')})",
    file=sys.stderr,
)
_inner_app = mcp.streamable_http_app()
app = _debug_asgi_app


# ── Stdio (cho CLI: uv run office-mcp) ──
def run_stdio():
    """Run as stdio MCP server (local subprocess)."""
    import sys
    print("[MCP-DEBUG] Starting stdio transport...", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_stdio()


if __name__ == "__main__":
    run_stdio()
