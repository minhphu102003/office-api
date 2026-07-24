# Office-MCP: Template Document Generator

Generate documents (.docx, .xlsx, .pptx) from pre-existing templates by merging JSON data into {{placeholder}} markers.

## Tools Overview

| Tool | Purpose |
|------|---------|
| `list_templates` | List available templates |
| `upload_template` | Upload a file as template (base64) |
| `create_template` | Convert a raw file into template (find/replace → placeholder) |
| `delete_template` | Delete a template |
| `view_template` | Inspect template structure & placeholders |
| `create_doc` | Merge data into template → generate docx |
| `fill_table_rows` | Clone table rows N times and fill placeholders |
| `generate_from_form` | Parse filled markdown form → auto run create_doc + fill_table_rows |
| `download_doc` | Download generated file as base64 |
| `create_draft` / `update_draft` / `get_draft` / `list_drafts` / `delete_draft` / `generate_from_draft` | Incremental multi-step workflow |
| `markdown_to_template` | Convert markdown → .docx template |
| `get_doc_info` | Get stats/outline of a generated document |

## Resources

| URI | Description |
|-----|-------------|
| `skill://guide` | Full usage guide (this file) |
| `skill://format/word-format` | Word formatting standards (font, spacing, margins) |
| `template://{name}/form` | Generate a markdown data-entry form from any template's placeholders |

## When to Use

- User asks to create invoices, contracts, reports, letters from a template
- User provides partial data — use `create_draft` + `update_draft` to collect it gradually
- User wants a formatted document with all data ready — use `create_doc` directly

---

## Workflow A: Simple (no dynamic tables)

1. `list_templates` → see available templates
2. `view_template` → inspect placeholders
3. `create_doc(template, data, output_filename)` → merge data into template
4. `download_doc(output_filename)` → retrieve file

---

## Workflow B: Template from user's Word file + dynamic tables

Use when the user uploads a .docx that needs `{{placeholder}}` markers added.

### Step 1 — Create template
```python
# Preview placeholders to user first (agent reads doc, proposes replacements)
create_template(
    source="C:/Users/.../my_document.docx",
    output_filename="my_template.docx",
    replacements={
        "Acme Corp": "{{company_name}}",
        "John Doe": "{{full_name}}",
    }
)
```

### Step 2 — Generate initial document (fills non-table fields)
```python
create_doc(
    template="my_template",
    data={
        "week_range": "13/7/2026 – 19/7/2026",
        "full_name": "Nguyen Van A",
    },
    output_filename="output.docx"
)
```
→ Table `{{...}}` placeholders remain untouched.

### Step 3 — Fill dynamic table rows
```python
fill_table_rows(
    filepath="output.docx",
    table_index=0,
    rows=[
        {"project_name": "Chatbot", "progress_percent": "90",
         "task_bullets": "- Viet document\n- Kiem thu"},
        {"project_name": "Website", "progress_percent": "50",
         "task_bullets": "- Phan tich yeu cau\n- Thiet ke UI"},
    ]
)
```

### Step 4 — Download
```python
download_doc(filepath="output.docx")
```

---

## Workflow C: Markdown Form Round-Trip (recommended for complex docs)

Best for documents with many placeholders + multiple dynamic tables. Uses the `template://{name}/form` resource and `generate_from_form` tool.

### Step 1 — Agent reads the data-entry form
```python
# Read the form resource
read_mcp_resource("template://ke_hoach_cong_tac_template/form")
# Returns markdown with all placeholders listed in tables
```

### Step 2 — Agent writes the form to a local .md file
```python
# Agent uses write() to save the markdown to a file
write("fill_data.md", form_content)
```

### Step 3 — User fills the markdown form
```
## General Fields
| Placeholder | Value |
|-------------|-------|
| `{{last_week}}` | 26/2026 |
| `{{full_name:uppercase}}` | LE VAN A |

## Dynamic Tables
### Table 2
| `{{project_name}}` | `{{progress_percent}}` | `{{task_bullets}}` |
|---|---|---|
| Chatbot | 90 | - Task 1\n- Task 2 |
| Website | 50 | - Task A |
```

### Step 4 — Agent generates the document
```python
generate_from_form(
    template="ke_hoach_cong_tac_template",
    form_content=filled_markdown_content,
    output_filename="final_report.docx"
)
```
→ Automatically calls `create_doc` (general fields) + `fill_table_rows` (each dynamic table).

### Step 5 — Download
```python
download_doc(filepath="final_report.docx")
```

---

## Stateful Workflow (resumable drafts)
Use when data comes incrementally:
1. `create_draft(template)` → get `draft_id`
2. `update_draft(draft_id, data={"key": "val"})` — call multiple times
3. `generate_from_draft(draft_id, output_filename)` → final doc
4. `download_doc(output_filename)` → retrieve

---

## Table Design Rules (for fill_table_rows)
- **Row 0**: header row (static text, no placeholders)
- **Row 1**: exactly 1 data template row with `{{placeholder}}` markers
- The template row is automatically cloned N times then removed

Common placeholders: `{{project_name}}`, `{{progress_percent}}`, `{{task_bullets}}`

Multi-line values use `\n` — auto-converted to Word `<w:br/>` line breaks.

---

## Template Form Resource
`template://{name}/form` returns a markdown document listing every `{{...}}` in the template, organized by location. The format is designed for `generate_from_form` to parse.

Usage:
```python
read_mcp_resource("template://ke_hoach_cong_tac_template/form")
```

---

## When NOT to use
- User wants a fully custom document from scratch — use the REST API endpoints instead
