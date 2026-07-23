---
name: office-mcp
description: Generate documents (.docx, .xlsx, .pptx) from templates via OfficeCLI. Use when user asks to create invoices, contracts, reports, or any document from a pre-existing template.
version: 1.0.0
---

# Office-MCP: Template Document Generator

## When to use this MCP

Call these tools when the user wants to **create a document from a template**:
- "Generate an invoice for Acme Corp, $5,200"
- "Create a contract for client Nguyen Van A"
- "Fill the Q4 report template with these numbers"
- "Produce a purchase order from the standard template"

**Do NOT use** when the user wants a fully custom document from scratch — use the `/api/v1/documents/*` REST endpoints for that.

## How it works

This MCP provides tools around a `templates/` folder. Each template is a regular `.docx`, `.xlsx`, or `.pptx` file with `{{placeholder}}` markers. The merge command replaces those markers with values from a JSON object.

Drafts are stored in SQLite (`output/drafts.db`) so work can be resumed across sessions.

## Workflow: stateful (recommended for partial data)

```
1. list_templates()               → see what templates exist
2. view_template(name)            → inspect placeholders
3. create_draft(template)         → start a draft → get draft_id
4. update_draft(draft_id, data)   → fill data gradually (call multiple times)
5. generate_from_draft(id, file)  → produce final document
6. download_doc(file)             → retrieve file as base64 → save to user's machine
```

Use `list_drafts()` to find in-progress drafts, `get_draft(id)` to check what's been filled.

## Workflow: stateless (simple, all data at once)

```
1. list_templates()               → see what templates exist
2. view_template(name)            → inspect placeholders
3. create_doc(name, data, file)   → merge & generate
4. download_doc(file)             → retrieve file as base64
```

## Example

User: *"Create an invoice for Acme Corp"* (partial data — use draft)

1. `list_templates()` → sees `invoice_template.docx`
2. `view_template("invoice_template")` → finds placeholders: `{{client_name}}`, `{{total}}`, `{{date}}`, `{{item}}`
3. `create_draft("invoice_template", {"client_name": "Acme Corp"})` → draft_id "abc123"
4. User adds total: `update_draft("abc123", {"total": "$5,200"})`
5. User adds date: `update_draft("abc123", {"date": "2026-07-22"})`
6. `generate_from_draft("abc123", "invoice_acme.docx")` → file created
7. `download_doc("invoice_acme.docx")` → get base64 → save locally

## Tools

| Tool | Purpose |
|------|---------|
| `list_templates` | List all available templates |
| `view_template` | Show text content and placeholders in a template |
| `create_doc` | Merge JSON data into a template, produce output file |
| `upload_template` | Upload a new template (base64) |
| `get_doc_info` | Read stats and outline of a generated file |
| `download_doc` | Get generated file as base64 for local saving |
| `create_draft` | Start a new draft, get draft_id |
| `update_draft` | Merge data into an existing draft |
| `get_draft` | View current state of a draft |
| `list_drafts` | List all drafts, filter by status |
| `delete_draft` | Remove a draft |
| `generate_from_draft` | Finalize a draft into a document |

## Notes

- Templates live in `templates/` and generated files go to `output/`
- Drafts persist in `output/drafts.db` (SQLite) across restarts
- Supported formats: `.docx`, `.xlsx`, `.pptx`
- The `--json` flag is always used for structured output
- If the user provides incomplete data, prefer `create_draft` + `update_draft` over `create_doc`
