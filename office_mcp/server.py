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

INSTRUCTIONS_PATH = Path(__file__).parent / "INSTRUCTIONS.md"
INSTRUCTIONS = INSTRUCTIONS_PATH.read_text()

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

from office_mcp.core.debug_middleware import wrap_asgi_app


# ── Streamable HTTP (cho Grok, opencode,...) ──
mcp.settings.streamable_http_path = "/"
print(
    f"[MCP-DEBUG] FastMCP instructions field: {mcp._mcp_server.instructions is not None}"
    f" (len={len(mcp._mcp_server.instructions or '')})",
    file=sys.stderr,
)
_inner_app = mcp.streamable_http_app()
app = wrap_asgi_app(_inner_app)


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
