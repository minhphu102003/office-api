from pathlib import Path
from mcp.server.fastmcp import FastMCP
from office_mcp.tools.templates import list_templates, upload_template
from office_mcp.tools.documents import create_doc, view_template
from office_mcp.tools.info import get_doc_info

INSTRUCTIONS = """# Office-MCP: Template Document Generator

Generate documents (.docx, .xlsx, .pptx) from pre-existing templates by merging JSON data into {{placeholder}} markers.

## Workflow
1. Call `list_templates` to see available templates
2. Call `view_template` on a template to inspect its placeholders
3. Determine the JSON data based on user's request
4. Call `create_doc` to merge data into template and produce output

## When to use
- User asks to create invoices, contracts, reports, letters from a template
- User provides data (client name, amounts, dates) and wants a formatted document

## When NOT to use
- User wants a fully custom document from scratch — use the REST API endpoints instead
"""

mcp = FastMCP("office-mcp", instructions=INSTRUCTIONS)

mcp.add_tool(list_templates)
mcp.add_tool(upload_template)
mcp.add_tool(create_doc)
mcp.add_tool(view_template)
mcp.add_tool(get_doc_info)

SKILL_PATH = Path(__file__).parent / "SKILL.md"
if SKILL_PATH.exists():
    skill_content = SKILL_PATH.read_text()
    mcp.add_resource(
        "skill://guide",
        name="MCP Server Guide",
        description="Full usage guide for office-mcp server, including workflows and examples",
        mime_type="text/markdown",
        content=skill_content,
    )

app = mcp.sse_app()
