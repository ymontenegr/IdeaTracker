"""
PDF generation using ReportLab.
Provides two reports:
  - generate_detail_report(idea) -> bytes
  - generate_monthly_report(ideas, month, year) -> bytes
"""

from io import BytesIO
from datetime import datetime
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable

from .models import Idea
from .config import STATUS_COLORS, PRIORIDAD_COLORS


# ── Color helpers ─────────────────────────────────────────────────────────

def _hex_to_color(hex_str: str) -> colors.Color:
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return colors.Color(r / 255, g / 255, b / 255)


BRAND_BLUE = _hex_to_color("#1A237E")
LIGHT_GREY = _hex_to_color("#F5F5F5")
BORDER_GREY = _hex_to_color("#E0E0E0")
WHITE = colors.white
BLACK = colors.black


# ── Status circle flowable ────────────────────────────────────────────────

class StatusCircle(Flowable):
    """A small colored circle used as status indicator."""

    def __init__(self, color_hex: str, label: str, size: float = 10):
        super().__init__()
        self._color = _hex_to_color(color_hex)
        self._label = label
        self._size = size
        self.width = size + 6 + len(label) * 6
        self.height = size + 4

    def draw(self):
        self.canv.setFillColor(self._color)
        r = self._size / 2
        self.canv.circle(r, r + 2, r, fill=1, stroke=0)
        self.canv.setFillColor(BLACK)
        self.canv.setFont("Helvetica-Bold", 9)
        self.canv.drawString(self._size + 6, 4, self._label)


# ── Style helpers ─────────────────────────────────────────────────────────

def _make_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Normal"],
            fontSize=20, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_LEFT,
            leading=24,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=11, textColor=colors.Color(0.8, 0.8, 1),
            fontName="Helvetica", alignment=TA_LEFT,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Normal"],
            fontSize=11, textColor=BRAND_BLUE,
            fontName="Helvetica-Bold",
            spaceBefore=8, spaceAfter=4,
        ),
        "label": ParagraphStyle(
            "label", parent=base["Normal"],
            fontSize=9, textColor=colors.Color(0.4, 0.4, 0.4),
            fontName="Helvetica-Bold",
        ),
        "value": ParagraphStyle(
            "value", parent=base["Normal"],
            fontSize=10, textColor=colors.Color(0.1, 0.1, 0.1),
            fontName="Helvetica", leading=14,
        ),
        "note_date": ParagraphStyle(
            "note_date", parent=base["Normal"],
            fontSize=8, textColor=colors.Color(0.5, 0.5, 0.5),
            fontName="Helvetica-Oblique",
        ),
        "note_text": ParagraphStyle(
            "note_text", parent=base["Normal"],
            fontSize=10, textColor=BLACK,
            fontName="Helvetica", leading=14,
        ),
        "table_header": ParagraphStyle(
            "table_header", parent=base["Normal"],
            fontSize=8, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell", parent=base["Normal"],
            fontSize=8, textColor=BLACK,
            fontName="Helvetica", leading=11,
        ),
        "table_cell_center": ParagraphStyle(
            "table_cell_center", parent=base["Normal"],
            fontSize=8, textColor=BLACK,
            fontName="Helvetica", leading=11, alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontSize=8, textColor=colors.Color(0.6, 0.6, 0.6),
            fontName="Helvetica", alignment=TA_CENTER,
        ),
        "report_title": ParagraphStyle(
            "report_title", parent=base["Normal"],
            fontSize=16, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
    }


def _header_table(title_text: str, subtitle_text: str = "") -> Table:
    """Blue header banner."""
    styles = _make_styles()
    title_p = Paragraph(title_text, styles["title"])
    rows = [[title_p]]
    if subtitle_text:
        rows.append([Paragraph(subtitle_text, styles["subtitle"])])

    t = Table(rows, colWidths=[A4[0] - 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return t


def _field_row(label: str, value: str, styles: dict) -> Table:
    """Two-cell row: label | value."""
    label_p = Paragraph(label.upper(), styles["label"])
    value_p = Paragraph(str(value) if value else "—", styles["value"])
    t = Table([[label_p, value_p]], colWidths=[3.5 * cm, 13 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _status_badge_paragraph(estatus: str, styles: dict) -> Paragraph:
    color_hex = STATUS_COLORS.get(estatus, "#888888")
    html = (
        f'<font color="{color_hex}"><b>●</b></font>'
        f'  <font color="#333333">{estatus}</font>'
    )
    return Paragraph(html, styles["value"])


def _prioridad_paragraph(prioridad: str, styles: dict) -> Paragraph:
    color_hex = PRIORIDAD_COLORS.get(prioridad, "#888888")
    html = f'<font color="{color_hex}"><b>{prioridad}</b></font>'
    return Paragraph(html, styles["value"])


# ── Report 1: Detail ──────────────────────────────────────────────────────

def generate_detail_report(idea: Idea) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        title=f"Reporte — {idea.nombre}",
    )
    styles = _make_styles()
    story = []

    # Header banner
    story.append(_header_table(
        idea.nombre,
        f"Reporte Detallado  ·  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ))
    story.append(Spacer(1, 0.4 * cm))

    # Status + Priority row
    status_color = STATUS_COLORS.get(idea.estatus, "#888888")
    prio_color = PRIORIDAD_COLORS.get(idea.prioridad, "#888888")

    badge_data = [[
        Paragraph(
            f'<font color="{status_color}"><b>●</b></font>  '
            f'<font color="#333333" size="11"><b>{idea.estatus}</b></font>',
            styles["value"]
        ),
        Paragraph(
            f'Prioridad: <font color="{prio_color}"><b>{idea.prioridad}</b></font>',
            styles["value"]
        ),
        Paragraph(
            f'Categoría: <b>{idea.categoria_nombre}</b>',
            styles["value"]
        ),
    ]]
    badge_t = Table(badge_data, colWidths=[5.5 * cm, 5 * cm, 6 * cm])
    badge_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEAFTER", (0, 0), (1, 0), 0.5, BORDER_GREY),
    ]))
    story.append(badge_t)
    story.append(Spacer(1, 0.5 * cm))

    # ── General Info section ──────────────────────────────
    story.append(Paragraph("Información General", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 0.2 * cm))

    story.append(_field_row("Descripción", idea.descripcion, styles))
    story.append(_field_row("Origen", idea.origen, styles))
    story.append(_field_row("Fecha de Registro", idea.fecha_registro_display(), styles))
    story.append(_field_row("Fecha Probable de Inicio", idea.fecha_inicio_display(), styles))

    story.append(Spacer(1, 0.4 * cm))

    # ── Financial section ─────────────────────────────────
    story.append(Paragraph("Datos Financieros", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 0.2 * cm))

    story.append(_field_row("Costo Aproximado", idea.costo_display(), styles))
    story.append(_field_row("Beneficio Esperado", idea.beneficio_esperado, styles))
    story.append(Spacer(1, 0.4 * cm))

    # ── Notes ──────────────────────────────────────────────
    story.append(Paragraph(f"Notas / Observaciones  ({len(idea.notas)})", styles["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY))
    story.append(Spacer(1, 0.2 * cm))

    if idea.notas:
        for nota in idea.notas:
            note_block = [
                [
                    Paragraph(nota.fecha_display(), styles["note_date"]),
                    Paragraph(nota.texto, styles["note_text"]),
                ]
            ]
            note_t = Table(note_block, colWidths=[3 * cm, 13.5 * cm])
            note_t.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDER_GREY),
            ]))
            story.append(note_t)
    else:
        story.append(Paragraph("Sin notas registradas.", styles["value"]))

    story.append(Spacer(1, 1 * cm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.3, color=BORDER_GREY))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"IdeaTracker  ·  Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()


# ── Report 2: Monthly ─────────────────────────────────────────────────────

def generate_monthly_report(ideas: List[Idea], month: int, year: int) -> bytes:
    buffer = BytesIO()
    month_name = datetime(year, month, 1).strftime("%B %Y").capitalize()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        title=f"Reporte Mensual — {month_name}",
    )
    styles = _make_styles()
    story = []

    # Header
    story.append(_header_table(
        f"Reporte Mensual — {month_name}",
        f"Total de ideas: {len(ideas)}  ·  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ))
    story.append(Spacer(1, 0.5 * cm))

    if not ideas:
        story.append(Paragraph("No hay ideas registradas para este período.", styles["value"]))
    else:
        # Sort by registration date
        ideas_sorted = sorted(ideas, key=lambda i: i.fecha_registro)

        # Table headers
        col_headers = [
            Paragraph("Fecha\nRegistro", styles["table_header"]),
            Paragraph("Nombre / Tema", styles["table_header"]),
            Paragraph("Categoría", styles["table_header"]),
            Paragraph("Descripción", styles["table_header"]),
            Paragraph("Fecha\nInicio", styles["table_header"]),
            Paragraph("Costo\nAprox.", styles["table_header"]),
            Paragraph("Beneficio\nEsperado", styles["table_header"]),
            Paragraph("Estatus", styles["table_header"]),
        ]

        col_widths = [1.9 * cm, 3.2 * cm, 2.3 * cm, 3.5 * cm,
                      1.9 * cm, 1.8 * cm, 3.2 * cm, 2.0 * cm]

        table_data = [col_headers]

        for idea in ideas_sorted:
            status_color = STATUS_COLORS.get(idea.estatus, "#888888")
            status_p = Paragraph(
                f'<font color="{status_color}"><b>●</b></font> {idea.estatus}',
                styles["table_cell"]
            )

            row = [
                Paragraph(idea.fecha_registro_display(), styles["table_cell_center"]),
                Paragraph(idea.nombre, styles["table_cell"]),
                Paragraph(idea.categoria_nombre, styles["table_cell"]),
                Paragraph(idea.descripcion[:120] + ("…" if len(idea.descripcion) > 120 else ""),
                          styles["table_cell"]),
                Paragraph(idea.fecha_inicio_display(), styles["table_cell_center"]),
                Paragraph(idea.costo_display(), styles["table_cell_center"]),
                Paragraph(idea.beneficio_esperado[:100] + ("…" if len(idea.beneficio_esperado) > 100 else ""),
                          styles["table_cell"]),
                status_p,
            ]
            table_data.append(row)

        tbl = Table(table_data, colWidths=col_widths, repeatRows=1)

        row_count = len(table_data)
        tbl.setStyle(TableStyle([
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            # Alternating rows
            *[("BACKGROUND", (0, i), (-1, i), LIGHT_GREY)
              for i in range(2, row_count, 2)],
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER_GREY),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, BRAND_BLUE),
        ]))

        story.append(tbl)

    story.append(Spacer(1, 0.8 * cm))

    # Summary stats
    if ideas:
        by_status: dict = {}
        for idea in ideas:
            by_status[idea.estatus] = by_status.get(idea.estatus, 0) + 1

        summary_rows = [
            [Paragraph("Resumen por Estatus", styles["table_header"]),
             Paragraph("Cantidad", styles["table_header"])]
        ]
        for estatus, cnt in sorted(by_status.items()):
            color = STATUS_COLORS.get(estatus, "#888888")
            summary_rows.append([
                Paragraph(f'<font color="{color}"><b>●</b></font>  {estatus}',
                          styles["table_cell"]),
                Paragraph(str(cnt), styles["table_cell_center"]),
            ])

        summary_t = Table(summary_rows, colWidths=[6 * cm, 2 * cm])
        summary_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("GRID", (0, 0), (-1, -1), 0.3, BORDER_GREY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(KeepTogether([
            Paragraph("Resumen", styles["section"]),
            HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY),
            Spacer(1, 0.2 * cm),
            summary_t,
        ]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.3, color=BORDER_GREY))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"IdeaTracker  ·  Reporte mensual {month_name}  ·  "
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        styles["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()
