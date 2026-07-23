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

## Workflow

```
1. list_templates()         → see what templates exist
2. view_template(name)      → inspect placeholders in a template
3. (you figure out the data based on user request)
4. create_doc(name, data, output)  → merge & generate
```

## Example

User: *"Create an invoice for Acme Corp, total $5,200"*

1. `list_templates()` → sees `invoice_template.docx`
2. `view_template("invoice_template")` → finds placeholders: `{{client_name}}`, `{{total}}`, `{{date}}`
3. Determines data: `{"client_name": "Acme Corp", "total": "$5,200", "date": "2026-07-22"}`
4. `create_doc("invoice_template", {...}, "invoice_acme.docx")`
5. Returns: *"Created invoice_acme.docx for Acme Corp, $5,200"*

## Tools

| Tool | Purpose |
|------|---------|
| `list_templates` | List all available templates |
| `view_template` | Show text content and placeholders in a template |
| `create_doc` | Merge JSON data into a template, produce output file |
| `upload_template` | Upload a new template (base64) |
| `get_doc_info` | Read stats and outline of a generated file |

## Notes

- Templates live in `templates/` and generated files go to `output/`
- Supported formats: `.docx`, `.xlsx`, `.pptx`
- The `--json` flag is always used for structured output
- If the user provides incomplete data, ask clarifying questions before calling `create_doc`
