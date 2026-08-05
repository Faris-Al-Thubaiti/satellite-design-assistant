"""PDF report generation for saved satellite recommendations."""

from __future__ import annotations

from html import escape
from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


NAVY = HexColor("#0B1F3A")
BLUE = HexColor("#2563EB")
CYAN = HexColor("#14B8A6")
PALE = HexColor("#EFF6FF")
SLATE = HexColor("#475569")


def _text(value: Any) -> str:
    return escape(str(value))


def _number(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _bullet_paragraphs(items: Iterable[Any], style: ParagraphStyle) -> list[Any]:
    flowables: list[Any] = []
    for item in items:
        if isinstance(item, dict):
            if "subsystem" in item:
                parts = (item.get("subsystem"), item.get("reason"))
            elif "payload_type" in item:
                parts = (item.get("payload_type"), item.get("use_when"))
            elif "condition" in item:
                parts = (item.get("condition"), item.get("recommendation"))
            else:
                parts = item.values()
            value = " - ".join(_text(part) for part in parts if part)
        else:
            value = _text(item)
        flowables.append(Paragraph(f"• {value}", style))
        flowables.append(Spacer(1, 0.8 * mm))
    return flowables


def _draw_page(canvas: Any, document: Any) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(CYAN)
    canvas.setLineWidth(1)
    canvas.line(18 * mm, 15 * mm, width - 18 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(18 * mm, 10 * mm, "Satellite Design Assistant")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


def generate_report(mission: dict[str, Any]) -> bytes:
    """Create a complete in-memory PDF for one saved mission."""

    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title=f"Satellite Design Recommendation {mission['mission_id']}",
        author="Satellite Design Assistant",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )
    subtitle = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=SLATE,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )
    heading = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=BLUE,
        spaceBefore=3 * mm,
        spaceAfter=2 * mm,
    )
    body = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=NAVY,
        spaceAfter=3 * mm,
    )
    bullet = ParagraphStyle(
        "ReportBullet",
        parent=body,
        leftIndent=5 * mm,
        firstLineIndent=-3 * mm,
        spaceAfter=0,
    )

    recommendation = mission["ai_recommendation"]
    knowledge = mission["engineering_knowledge"] or {}
    story: list[Any] = [
        Paragraph("Satellite Design Recommendation", title),
        Paragraph(
            f"Mission #{mission['mission_id']} • Generated from a saved analysis",
            subtitle,
        ),
        Paragraph("Mission brief", heading),
        Paragraph(_text(mission["mission_description"]), body),
    ]

    summary_data = [
        ["Design field", "Recommendation"],
        ["Mission type", _text(recommendation["mission_type"])],
        ["Orbit", _text(recommendation["recommended_orbit"])],
        ["Altitude", f"{_number(recommendation['altitude_km'])} km"],
        ["Payload", _text(recommendation["payload"])],
        ["Power", f"{_number(recommendation['power_watts'])} W"],
        ["Mass class", _text(recommendation["mass_class"])],
        ["Lifetime", f"{_number(recommendation['lifetime_years'])} years"],
        ["ADCS", _text(recommendation["adcs_type"])],
    ]
    summary_table = Table(summary_data, colWidths=[42 * mm, 122 * mm], repeatRows=1)
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (0, -1), PALE),
                ("TEXTCOLOR", (0, 1), (-1, -1), NAVY),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#CBD5E1")),
            ]
        )
    )
    story.extend(
        [
            Paragraph("Conceptual design", heading),
            summary_table,
            Paragraph("Engineering justification", heading),
            Paragraph(_text(recommendation["justification"]), body),
            PageBreak(),
            Paragraph("Engineering knowledge", title),
        ]
    )

    knowledge_sections = (
        ("Design drivers", "design_drivers"),
        ("Required subsystems", "required_subsystems"),
        ("Payload options", "payload_options"),
        ("Advantages", "advantages"),
        ("Limitations", "limitations"),
        ("Selection rules", "selection_rules"),
    )
    for label, key in knowledge_sections:
        story.append(Paragraph(label, heading))
        story.extend(_bullet_paragraphs(knowledge.get(key, []), bullet))

    document.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
    return output.getvalue()
