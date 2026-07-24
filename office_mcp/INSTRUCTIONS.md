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

## Table Row Cloning (fill_table_rows)
Use `fill_table_rows` when a table has dynamic rows (e.g. a weekly task list with 1+ projects).

Template design:
- **Row 0**: header row (static text, no placeholders)
- **Row 1**: data template row with `{{placeholder}}` markers
- Only **1 data row** in the template — it will be cloned N times

Common placeholders for data rows:
- `{{project_name}}` — project/task name
- `{{progress_percent}}` — completion percentage
- `{{task_bullets}}` — multi-line bullet list (each line starts with `- `)

Workflow:
1. `create_doc` (or `generate_from_draft`) to produce the initial .docx with 1 template row
2. Call `fill_table_rows(filepath="output.docx", rows=[...])` to clone and fill
3. `download_doc` to retrieve the final file

Example:
```
fill_table_rows(
    filepath="ke_hoach_cong_tac_output.docx",
    table_index=0,
    rows=[
        {"project_name": "Chatbot Tuyển Sinh", "progress_percent": "90", "task_bullets": "- Viết document\n- Kiểm thử dashboard"},
        {"project_name": "Website Tuyển Sinh", "progress_percent": "50", "task_bullets": "- Phân tích yêu cầu\n- Thiết kế UI"},
    ]
)
```

## When NOT to use
- User wants a fully custom document from scratch — use the REST API endpoints instead
