from datetime import datetime
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QGroupBox, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt

from ..data_manager import load_all_ideas, load_idea
from ..models import Idea


BTN_PRIMARY = """
QPushButton {
    background: #2196F3; color: white; border: none;
    border-radius: 6px; padding: 10px 22px; font-size: 14px; font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
QPushButton:disabled { background: #90CAF9; }
"""

COMBO_STYLE = """
QComboBox {
    border: 1px solid #CCCCCC; border-radius: 6px;
    padding: 8px 12px; font-size: 13px;
    background: #FFFFFF; color: #222222; min-width: 200px;
}
QComboBox:!editable { color: #222222; }
QComboBox:!editable:on { color: #222222; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background: #FFFFFF;
    color: #222222;
    selection-background-color: #E3F2FD;
    selection-color: #000000;
}
QComboBox QAbstractItemView::item { color: #222222; }
QComboBox QAbstractItemView::item:selected { color: #000000; }
"""

GROUP_STYLE = """
QGroupBox {
    font-size: 14px; font-weight: bold; color: #1A237E;
    border: 1px solid #E0E0E0; border-radius: 10px;
    margin-top: 14px; background: white;
    padding: 16px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px; top: 4px;
    padding: 0 6px;
    background: white;
}
"""


class ReportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._ideas: List[Idea] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 16, 24, 16)
        title = QLabel("Reportes")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A237E;")
        hh.addWidget(title)
        layout.addWidget(header)

        # Content
        content = QWidget()
        content.setStyleSheet("background: #F5F7FA;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 32, 40, 32)
        cl.setSpacing(24)

        # ── Report 1: Detallado por Idea ─────────────────────
        grp1 = QGroupBox("📄  Reporte Detallado por Idea")
        grp1.setStyleSheet(GROUP_STYLE)
        g1l = QVBoxLayout(grp1)
        g1l.setSpacing(14)

        desc1 = QLabel(
            "Genera el reporte completo de una idea: todos sus campos, historial de notas "
            "y semáforo de estatus."
        )
        desc1.setStyleSheet("color: #555; font-size: 13px;")
        desc1.setWordWrap(True)
        g1l.addWidget(desc1)

        row1 = QHBoxLayout()
        lbl_idea = QLabel("Idea:")
        lbl_idea.setStyleSheet("font-size: 13px; color: #333; font-weight: normal;")
        row1.addWidget(lbl_idea)

        self.idea_combo = QComboBox()
        self.idea_combo.setStyleSheet(COMBO_STYLE)
        self.idea_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row1.addWidget(self.idea_combo)

        btn_detail = QPushButton("Ver Reporte")
        btn_detail.setStyleSheet(BTN_PRIMARY)
        btn_detail.clicked.connect(self._preview_detail)
        row1.addWidget(btn_detail)
        g1l.addLayout(row1)

        cl.addWidget(grp1)

        # ── Report 2: Mensual ────────────────────────────────
        grp2 = QGroupBox("📊  Reporte Mensual de Ideas")
        grp2.setStyleSheet(GROUP_STYLE)
        g2l = QVBoxLayout(grp2)
        g2l.setSpacing(14)

        desc2 = QLabel(
            "Genera un resumen tabular con todas las ideas registradas en un mes/año específico."
        )
        desc2.setStyleSheet("color: #555; font-size: 13px;")
        desc2.setWordWrap(True)
        g2l.addWidget(desc2)

        row2 = QHBoxLayout()
        lbl_mes = QLabel("Mes:")
        lbl_mes.setStyleSheet("font-size: 13px; color: #333; font-weight: normal;")
        row2.addWidget(lbl_mes)

        self.mes_combo = QComboBox()
        self.mes_combo.setStyleSheet(COMBO_STYLE)
        row2.addWidget(self.mes_combo)

        row2.addStretch()

        btn_monthly = QPushButton("Ver Reporte")
        btn_monthly.setStyleSheet(BTN_PRIMARY)
        btn_monthly.clicked.connect(self._preview_monthly)
        row2.addWidget(btn_monthly)
        g2l.addLayout(row2)

        cl.addWidget(grp2)
        cl.addStretch()
        layout.addWidget(content)

        self.refresh()

    def refresh(self):
        self._ideas = load_all_ideas()
        self._populate_idea_combo()
        self._populate_month_combo()

    def _populate_idea_combo(self):
        self.idea_combo.clear()
        ideas_sorted = sorted(self._ideas, key=lambda i: i.nombre.lower())
        for idea in ideas_sorted:
            self.idea_combo.addItem(idea.nombre, idea.id)
        if not ideas_sorted:
            self.idea_combo.addItem("(No hay ideas registradas)", None)

    def _populate_month_combo(self):
        self.mes_combo.clear()
        months = sorted(set(i.mes_registro() for i in self._ideas), reverse=True)
        for year, month in months:
            if year == 0:
                continue
            label = datetime(year, month, 1).strftime("%B %Y").capitalize()
            self.mes_combo.addItem(label, (year, month))
        if not months or all(y == 0 for y, m in months):
            self.mes_combo.addItem("(No hay datos)", None)

    def _preview_detail(self):
        idea_id = self.idea_combo.currentData()
        if not idea_id:
            QMessageBox.information(self, "Sin ideas", "No hay ideas registradas.")
            return
        idea = load_idea(idea_id)
        if idea is None:
            QMessageBox.warning(self, "Error", "No se encontró la idea.")
            return

        from ..pdf_generator import generate_detail_report
        from .pdf_preview import PDFPreviewDialog

        try:
            pdf_bytes = generate_detail_report(idea)
        except Exception as e:
            QMessageBox.critical(self, "Error generando PDF", str(e))
            return

        dlg = PDFPreviewDialog(
            pdf_bytes=pdf_bytes,
            suggested_name=f"reporte_idea_{idea.nombre[:30].replace(' ', '_')}",
            parent=self,
        )
        dlg.exec()

    def _preview_monthly(self):
        mes_data = self.mes_combo.currentData()
        if not mes_data:
            QMessageBox.information(self, "Sin datos", "No hay datos para generar el reporte.")
            return
        year, month = mes_data
        ideas_mes = [i for i in self._ideas if i.mes_registro() == (year, month)]

        from ..pdf_generator import generate_monthly_report
        from .pdf_preview import PDFPreviewDialog

        try:
            pdf_bytes = generate_monthly_report(ideas_mes, month, year)
        except Exception as e:
            QMessageBox.critical(self, "Error generando PDF", str(e))
            return

        month_str = datetime(year, month, 1).strftime("%B_%Y")
        dlg = PDFPreviewDialog(
            pdf_bytes=pdf_bytes,
            suggested_name=f"reporte_mensual_{month_str}",
            parent=self,
        )
        dlg.exec()
