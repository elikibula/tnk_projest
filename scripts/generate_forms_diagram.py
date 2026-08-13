"""Generate a printable TNK section, form, field and relationship reference."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "tnk-17-sections-42-forms-diagram.pdf"
SCHEMA_CODE = r'''
import json, os, sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
import django
django.setup()
from apps.reporting.models import ReportSectionStatus
from apps.reporting.section_registry import SECTION_ENTRIES
labels = dict(ReportSectionStatus.Section.choices)
result = []
for section_code, section_label in ReportSectionStatus.Section.choices:
    forms = []
    for config in SECTION_ENTRIES.get(section_code, ()):
        fields = []
        configured = set(config.fields)
        for name in config.fields:
            field = config.model._meta.get_field(name)
            relation = field.related_model._meta.verbose_name.title() if getattr(field, "related_model", None) else ""
            fields.append({"name": name, "label": str(field.verbose_name).replace("_", " ").title(), "type": field.__class__.__name__.replace("Field", "") or "Field", "required": not field.blank and not field.null, "relation": relation})
        context = []
        for name in ("report", "village", "home_village", "reporting_period", "created_by", "updated_by"):
            if name in configured:
                continue
            try:
                field = config.model._meta.get_field(name)
            except Exception:
                continue
            target = field.related_model._meta.verbose_name.title() if getattr(field, "related_model", None) else field.__class__.__name__.replace("Field", "")
            context.append(f"{name} -> {target}")
        forms.append({"key": config.key, "label": config.label, "model": config.model._meta.label, "allow_create": config.allow_create, "fields": fields, "context": context})
    result.append({"code": section_code, "label": labels[section_code], "forms": forms})
print(json.dumps(result))
'''


def load_schema() -> list[dict]:
    python = ROOT / "tnk_venv" / "Scripts" / "python.exe"
    completed = subprocess.run([str(python), "-c", SCHEMA_CODE], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(completed.stdout)


base_styles = getSampleStyleSheet()
TITLE = ParagraphStyle("tnk_title", parent=base_styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=colors.HexColor("#0B4F4A"), alignment=TA_LEFT, spaceAfter=8)
SUBTITLE = ParagraphStyle("tnk_subtitle", parent=base_styles["Normal"], fontSize=9, leading=13, textColor=colors.HexColor("#526765"), spaceAfter=10)
SECTION = ParagraphStyle("tnk_section", parent=base_styles["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#0B4F4A"), spaceAfter=6)
FORM_TITLE = ParagraphStyle("tnk_form_title", parent=base_styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.white)
CELL = ParagraphStyle("tnk_cell", parent=base_styles["Normal"], fontSize=7, leading=8.7, textColor=colors.HexColor("#17312F"))
CELL_BOLD = ParagraphStyle("tnk_cell_bold", parent=CELL, fontName="Helvetica-Bold")
SMALL = ParagraphStyle("tnk_small", parent=base_styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#526765"))
NODE = ParagraphStyle("tnk_node", parent=base_styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#17312F"))


def para(text: str, style=CELL) -> Paragraph:
    return Paragraph(str(text), style)


def header_footer(canvas, doc):
    canvas.saveState()
    width, _height = landscape(A4)
    canvas.setStrokeColor(colors.HexColor("#DCE7E5"))
    canvas.line(15 * mm, 12 * mm, width - 15 * mm, 12 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#637573"))
    canvas.drawString(15 * mm, 7.5 * mm, "TNK Insight - Sections, forms and field relationships")
    page_text = f"Page {doc.page}"
    canvas.drawString(width - 15 * mm - stringWidth(page_text, "Helvetica", 7), 7.5 * mm, page_text)
    canvas.restoreState()


def overview_table(sections: list[dict]) -> Table:
    nodes = []
    for index, section in enumerate(sections, 1):
        count = len(section["forms"])
        suffix = f"{count} entry form{'s' if count != 1 else ''}" if count else "Workflow controls - outside the 42 forms"
        nodes.append(para(f"<b>{index}. {section['label']}</b><br/>{suffix}", NODE))
    while len(nodes) % 3:
        nodes.append("")
    table = Table([nodes[index:index + 3] for index in range(0, len(nodes), 3)], colWidths=[84 * mm] * 3, rowHeights=19 * mm, hAlign="LEFT")
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E8F5F2")), ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#86BDB5")), ("INNERGRID", (0, 0), (-1, -1), 2.2, colors.white), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    return table


def form_flowables(form: dict) -> list:
    relationship = "TNKReport -> ReportSectionStatus -> " + form["model"]
    mode = "Edit existing master record" if not form["allow_create"] else "Add or edit repeatable records"
    title = Table([[para(f"{form['label']}  [{form['model']}]", FORM_TITLE)]], colWidths=[252 * mm])
    title.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F766E")), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#0B4F4A")), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    context = ", ".join(form["context"]) if form["context"] else "No additional server-bound context"
    metadata = Table([[para(f"<b>Relationship:</b> {relationship}<br/><b>Mode:</b> {mode}<br/><b>Assigned automatically:</b> {context}", SMALL)]], colWidths=[252 * mm])
    metadata.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F7F6")), ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1E0DD")), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    rows = [[para("Field", CELL_BOLD), para("Data type", CELL_BOLD), para("Required", CELL_BOLD), para("Relationship", CELL_BOLD)]]
    for field in form["fields"]:
        rows.append([para(f"{field['label']}<br/><font color='#637573'>{field['name']}</font>"), para(field["type"]), para("Yes" if field["required"] else "No"), para(("-> " + field["relation"]) if field["relation"] else "-")])
    fields = Table(rows, colWidths=[95 * mm, 48 * mm, 28 * mm, 81 * mm], repeatRows=1, hAlign="LEFT")
    fields.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEBE8")), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CFDDDA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBFA")]), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    items = [title, metadata, fields, Spacer(1, 5 * mm)]
    return [KeepTogether(items)] if len(form["fields"]) <= 20 else items


def build_pdf(sections: list[dict]):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total_forms = sum(len(section["forms"]) for section in sections)
    total_fields = sum(len(form["fields"]) for section in sections for form in section["forms"])
    if len(sections) != 17 or total_forms != 42:
        raise ValueError(f"Expected 17 sections and 42 forms; found {len(sections)} and {total_forms}.")
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=landscape(A4), rightMargin=15 * mm, leftMargin=15 * mm, topMargin=14 * mm, bottomMargin=17 * mm, title="TNK Insight - 17 Sections and 42 Entry Forms", author="TNK Insight", subject="Printable section, form, field and model relationship reference")
    flow = [Paragraph("TNK Insight: 17 Sections and 42 Entry Forms", TITLE), Paragraph(f"Printable relationship diagram and field reference | 17 sections | 42 entry forms | {total_fields} configured form fields", SUBTITLE)]
    chain = Table([[para("TNKReport", CELL_BOLD), para("->", CELL_BOLD), para("17 section records", CELL_BOLD), para("->", CELL_BOLD), para("42 entry forms", CELL_BOLD), para("->", CELL_BOLD), para("Domain records", CELL_BOLD)]], colWidths=[42 * mm, 10 * mm, 60 * mm, 10 * mm, 58 * mm, 10 * mm, 62 * mm], rowHeights=13 * mm)
    chain.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#D8F4ED")), ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#E8F5F2")), ("BACKGROUND", (4, 0), (4, 0), colors.HexColor("#E8F5F2")), ("BACKGROUND", (6, 0), (6, 0), colors.HexColor("#D8F4ED")), ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#86BDB5")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (1, 0), (5, 0), "CENTER")]))
    flow.extend([chain, Spacer(1, 4 * mm), Paragraph("Legend: -> identifies a model relationship. Report, village and reporting period values shown as server-bound are assigned from the selected report and are not editable by the user. Evidence and Validation use dedicated workflow forms, outside the count of 42 configured entry forms.", SMALL), Spacer(1, 4 * mm), overview_table(sections)])
    for number, section in enumerate(sections, 1):
        flow.extend([PageBreak(), Paragraph(f"{number}. {section['label']}", SECTION), Paragraph(f"Section code: {section['code']} | TNKReport -> ReportSectionStatus ({section['code']}) -> {len(section['forms'])} configured entry form{'s' if len(section['forms']) != 1 else ''}", SUBTITLE)])
        if not section["forms"]:
            explanation = "Protected evidence upload, document linking and final declaration controls." if section["code"] == "evidence_declarations" else "Automated validation, data-quality issues, declaration, submission and approval workflow controls."
            workflow = Table([[para("Workflow-controlled section", FORM_TITLE)], [para(explanation, CELL)]], colWidths=[252 * mm])
            workflow.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")), ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FBFA")), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CFDDDA")), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
            flow.append(workflow)
        for form in section["forms"]:
            flow.extend(form_flowables(form))
    doc.build(flow, onFirstPage=header_footer, onLaterPages=header_footer)


if __name__ == "__main__":
    build_pdf(load_schema())
    print(OUTPUT)
