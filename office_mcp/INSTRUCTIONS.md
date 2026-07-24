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

## Templates with Dynamic Tables (create_template + fill_table_rows)
Use this flow when a document has both static placeholders AND a table with dynamic rows.

### Template Design
Create the template with `create_template`:
- Place all non-table text as `{{placeholder}}` (e.g. `{{week_range}}`, `{{reporter_name}}`)
- In the table: keep only **1 header row** + **1 data row** with `{{placeholder}}` markers
- The data row will be cloned N times by `fill_table_rows`

Common table placeholders:
- `{{project_name}}` — project/task name
- `{{progress_percent}}` — completion percentage  
- `{{task_bullets}}` — multi-line bullet list (use `\n` between lines)

### Full Workflow (step by step)
1. **Upload + create template**
   - Agent reads the user's Word file, proposes placeholders for approval
   - `delete_template(old_name)` if replacing an existing template
   - `upload_template(filename, base64_content)` to upload the user's formatted file
   - `create_template(source="filename.docx", output_filename="template.docx", replacements={...})`
   
2. **Generate initial doc** with `create_doc`
   - Fill ONLY the non-table placeholders (leave `{{project_name}}`, `{{task_bullets}}` etc. as-is)
   - `create_doc(template="template.docx", data={"week_range": "13/7 – 19/7/2026", "department_name": "..."}, output_filename="output.docx")`

3. **Fill table rows** with `fill_table_rows`
   - The output from step 2 still has `{{...}}` markers in the table row
   - `fill_table_rows(filepath="output.docx", table_index=0, rows=[{...}, {...}])`

4. **Download**
   - `download_doc(filepath="output.docx")` → base64 → save to user

### Example
```
# Step 2
create_doc(template="ke_hoach_cong_tac", data={
    "week_range": "13/7/2026 – 19/7/2026",
    "department_name": "Phòng Đào Tạo",
}, output_filename="baocao_tuan.docx")

# Step 3
fill_table_rows(filepath="baocao_tuan.docx", table_index=0, rows=[
    {"project_name": "Chatbot Tuyển Sinh", "progress_percent": "90", "task_bullets": "- Viết document\n- Kiểm thử dashboard"},
    {"project_name": "Website Tuyển Sinh", "progress_percent": "50", "task_bullets": "- Phân tích yêu cầu\n- Thiết kế UI"},
])
```

### Important Notes
- `create_doc` merge leaves unknown `{{...}}` untouched — safe to skip table placeholders
- `fill_table_rows` works on files in either templates/ or output/ directory
- Multi-line values use `\n` (literal newline) — auto-converted to Word line breaks

## When NOT to use
- User wants a fully custom document from scratch — use the REST API endpoints instead
