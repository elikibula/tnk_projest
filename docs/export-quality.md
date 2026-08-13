# PDF, Excel, and CSV export quality

Phase F keeps the existing `analytics:export` endpoint and its central role/location policy. All three formats build the same immutable `ExportDataset` after reapplying `can_export_report_summary` and `villages_for_user`; successful exports create both `DataExportAudit` and `AuditEvent` records.

## PDF decision

PDF generation uses ReportLab Platypus rather than hand-written PDF syntax. It provides A4 pagination, repeated table headings, wrapped paragraphs, PDF metadata, and `Page X of Y` footers. The document contains:

- report title and applied export scope;
- village, Tikina, province, reporting period and dates;
- report status, completion and data-quality score;
- approval history for users authorised to view detailed reports;
- approved-amendment history;
- non-personal IVDP project summaries, including numeric budgets;
- evidence references only when `can_view_document` authorises that document.

Analysts receive the scoped report-summary table only. Ordinary exports never include household-head names, person contacts, health/disability rows, community-safety detail, account detail, or evidence contents.

Unicode text uses a runtime TrueType font. Resolution order is:

1. `TNK_PDF_FONT_PATH` and `TNK_PDF_FONT_BOLD_PATH`;
2. deployment DejaVu Sans installed by the backend image;
3. Windows Arial for local Windows development;
4. ReportLab's bundled Bitstream Vera fallback.

No font is stored as a project artifact. A missing Unicode font raises an actionable configuration error instead of silently falling back to Helvetica.

## Excel

Excel output uses `openpyxl` and contains readable styled headings, filters, frozen header rows, column widths, real numeric and date cells, and an `Export information` worksheet showing scope, reason, generation time, and record count. When the user may view the IVDP section, a Projects worksheet retains budgets and percentages as numeric cells and dates as real date cells. Currency is explicitly formatted as FJD.

Every user-controlled text cell is neutralised when its first non-space character is `=`, `+`, `-`, or `@`. Restricted personal columns are not selected at all.

## CSV

CSV output includes a UTF-8 byte-order mark for reliable Unicode display in common spreadsheet applications. It uses the same scoped columns and formula-injection neutralisation as Excel. Dates are emitted in ISO form by Python's CSV conversion.

## Export size and future background execution

Exports remain synchronous because their present grain is a filtered quarterly report summary and the controlled deployment volume has not justified an operational queue. The pure `build_export_dataset` and `build_pdf_bytes` boundaries separate database selection from rendering, so a future worker can reuse the exact security-filtered payload and renderer without changing file semantics. Phase H must benchmark province- and national-scale fixtures and define a queue threshold before broad production use. Celery was not introduced solely for Phase F.

## Verification

Automated tests cover Unicode macrons, long village/project names, multi-page PDF generation, page numbers, approval history, evidence references, analyst detail suppression, excluded household names, Excel numeric/date types, money cells, headings, filters, freeze panes, CSV BOM, formula injection, applied filters, and export auditing. A representative three-page PDF was also rendered to PNG with Poppler and visually inspected for clipping, overlap, wrapping, glyph defects, table readability, and footer placement.
