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

This MCP provides **2 ways** to create templates:

1. **`create_template`** — from an existing Office file (preserves original formatting)
2. **`markdown_to_template`** — from markdown text (generates fresh .docx with proper formatting)

Neither tool uses AI. The agent is responsible for analysis, reasoning, and user interaction.

Drafts are stored in SQLite (`output/drafts.db`) so work can be resumed across sessions.

## Workflow A: Create template from existing file (preserve formatting)

```
1. User provides a document (docx/xlsx/pptx)
2. Agent reads the file locally → extracts text for analysis
3. Agent identifies dynamic content → creates markdown preview showing proposed {{placeholders}}
4. User approves the markdown
5. Agent calls create_template(
       source="C:/path/to/original.docx",
       output_filename="contract_template.docx",
       replacements={"Acme Corp": "{{company_name}}", "John Doe": "{{client_name}}"}
   )
   → MCP: copies file → officecli batch find/replace → preserves all formatting
6. list_templates() → sees the new template
7. create_doc / create_draft → use the template as normal
```

## Workflow B: Create template from markdown (new document)

```
1. Agent/User composes markdown with headings, lists, bold, {{placeholders}}...
2. Agent calls markdown_to_template(markdown="...", output_filename="report_template.docx")
   → MCP: python-docx → creates formatted .docx (TNR 12pt, 1.5 spacing, justified, etc.)
3. list_templates() → sees the new template
4. view_template("report_template") → inspect placeholders
5. create_doc / create_draft → use as normal
```

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
| `create_template` | Create template from existing file: copy + find/replace placeholders (preserves original formatting) |
| `markdown_to_template` | Convert markdown text to a formatted .docx template (TNR, 1.5 spacing, word-format standards) |
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
