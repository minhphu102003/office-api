# Office-MCP: Template Document Generator

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
