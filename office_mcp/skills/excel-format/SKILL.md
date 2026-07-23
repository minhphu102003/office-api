---
name: excel-format
description: Use when creating or formatting .xlsx spreadsheets. Covers fonts, alignment, table structures, colors, number formats, page setup, and professional Excel best practices. Trigger: excel, xlsx, spreadsheet, sheet, table, data, report, dashboard.
---

# Excel Formatting Standards

Professional formatting guidelines for .xlsx spreadsheets. Apply these standards when creating templates or instructing users.

## Font

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Header row | Calibri | 12pt | Bold |
| Body data | Calibri | 11pt | Regular |
| Titles | Calibri | 14-16pt | Bold |
| Subtotals | Calibri | 11pt | Bold |
| Notes | Calibri | 9-10pt | Regular |

- Use clean sans-serif fonts (Calibri, Arial, Segoe UI)
- Maintain consistent font throughout the workbook
- Avoid fonts below 9pt for print readability
- Use italic for notes or estimated values

## Alignment

| Data Type | Alignment |
|-----------|-----------|
| Text | Left-aligned |
| Numbers | Right-aligned |
| Headers | Center-aligned |
| Dates | Center or right-aligned |
| Currency | Right-aligned, decimal points aligned |

- Do not merge cells for layout — use Center Across Selection instead
- Use Wrap Text for multi-line headers
- Keep row heights auto-adjusted to content

## Table Structure

- Use Excel Tables (Ctrl+T) for all data ranges — auto-expand, filter, structured references
- One logical table per sheet
- Flat structure: one header row, one record per row
- No merged cells in data areas
- No blank rows or columns within data
- No subtotal rows inside the data — use Total Row (Table Design tab)
- Name every table (Table Design > Table Name) with meaningful names (e.g., `Sales`, `Orders`)

## Colors & Themes

- Maximum 3-4 colors in palette
- Header row: Dark background (navy #1F3864, charcoal #333333) with white text
- Banded rows: Alternating white/light gray (#F2F2F2) for readability
- Accent color: Use sparingly for KPIs or key metrics
- Use built-in cell styles (Title, Heading 1, Total) for consistency
- Save custom themes for reuse (Page Layout > Themes > Save Current Theme)

## Number Formats

- **Currency:** `$#,##0.00` (USD) — consistent symbol throughout
- **Percentages:** `0.00%` — aligned decimal points
- **Dates:** `YYYY-MM-DD` or `DD/MM/YYYY` — consistent across workbook
- **Thousands separator:** `#,##0` for large numbers
- **Decimal places:** Consistent precision within each column
- Avoid general format for financial data

## Borders & Gridlines

- Print gridlines: Off
- Screen gridlines: Keep on (or light gray)
- Use thin borders (`------`) for data areas
- Use thicker borders for section separators
- Avoid excessive borders — minimal is more professional
- Use top/bottom borders for summary rows

## Conditional Formatting

- Use sparingly — highlight only what matters
- Color scales: Green-Yellow-Red for performance metrics
- Data bars: For comparison across rows
- Icon sets: Only for clear binary/ternary indicators
- Clear rules when no longer needed to avoid performance issues

## Page Setup

- **Orientation:** Portrait for data sheets; Landscape for wide tables
- **Margins:** Normal (0.75 inch top/bottom, 0.7 inch left/right)
- **Print area:** Define explicitly
- **Print titles:** Repeat header rows on every page
- **Page breaks:** Insert at logical section boundaries
- **Scaling:** Fit to 1 page wide, as many pages tall as needed
- **Headers/Footers:** Sheet name, date, page numbers

## Best Practices

- Freeze panes at header row for navigation
- Use Data Validation for input constraints (dropdowns, ranges)
- Use Named Ranges for key cells or formulas
- Document assumptions in a separate Notes sheet
- Remove unused rows/columns before finalizing
- Use consistent column widths (auto-fit)
- Protect formula cells from accidental edits
- Keep raw data and presentation on separate sheets
