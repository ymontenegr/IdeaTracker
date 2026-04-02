from datetime import datetime
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QMessageBox, QAbstractItemView, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QBrush

from ..data_manager import load_all_tareas, load_all_ideas, delete_tarea
from ..models import Tarea
from ..config import TAREA_STATUS_LIST, TAREA_STATUS_COLORS, IDEA_DEFAULT_ID, IDEA_DEFAULT_NAME


TABLE_STYLE = """
QTableWidget {
    background: #FFFFFF; color: #222222;
    border: none; gridline-color: #F0F0F0; font-size: 13px;
    selection-background-color: #E3F2FD; selection-color: #000000;
    alternate-background-color: #FAFAFA;
}
QTableWidget::item { padding: 6px 10px; border-bottom: 1px solid #F5F5F5; color: #222222; }
QTableWidget::item:selected { background: #E3F2FD; color: #000000; }
QHeaderView::section {
    background: #F8F9FA; color: #555555; font-weight: bold;
    font-size: 12px; padding: 8px 10px; border: none;
    border-bottom: 2px solid #E0E0E0; border-right: 1px solid #E8E8E8;
}
"""

BTN_PRIMARY = """
QPushButton {
    background: #2196F3; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 8px 18px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
"""

BTN_SECONDARY = """
QPushButton {
    background: #FFFFFF; color: #333333; border: 1px solid #CCCCCC;
    border-radius: 6px; padding: 6px 14px; font-size: 12px;
}
QPushButton:hover { background: #F5F5F5; }
"""

BTN_DANGER = """
QPushButton {
    background: #E53935; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 6px 14px; font-size: 12px;
}
QPushButton:hover { background: #C62828; }
"""

COMBO_STYLE = """
QComboBox {
    border: 1px solid #CCCCCC; border-radius: 6px; padding: 6px 10px;
    font-size: 13px; background: #FFFFFF; color: #222222; min-width: 140px;
}
QComboBox:!editable { color: #222222; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC; background: #FFFFFF; color: #222222;
    selection-background-color: #E3F2FD; selection-color: #000000;
}
"""

SEARCH_STYLE = """
QLineEdit {
    border: 1px solid #CCCCCC; border-radius: 6px;
    padding: 6px 12px; font-size: 13px; background: #FFFFFF;
    color: #222222; min-width: 200px;
}
"""


class TareasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._all_tareas: List[Tarea] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 16, 24, 16)
        title = QLabel("Tareas")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A237E;")
        hh.addWidget(title)
        hh.addStretch()
        self.btn_new = QPushButton("+ Nueva Tarea")
        self.btn_new.setStyleSheet(BTN_PRIMARY)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        hh.addWidget(self.btn_new)
        layout.addWidget(header)

        # ── Filters toolbar ──────────────────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(24, 10, 24, 10)
        tb.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por nombre...")
        self.search_input.setStyleSheet(SEARCH_STYLE)
        tb.addWidget(self.search_input)
        tb.addStretch()

        lbl = QLabel("Filtrar:")
        lbl.setStyleSheet("color: #666666; font-size: 13px;")
        tb.addWidget(lbl)

        self.filter_estatus = QComboBox()
        self.filter_estatus.setStyleSheet(COMBO_STYLE)
        self.filter_estatus.addItem("Todos los estatus", None)
        for s in TAREA_STATUS_LIST:
            self.filter_estatus.addItem(s, s)
        tb.addWidget(self.filter_estatus)

        self.filter_idea = QComboBox()
        self.filter_idea.setStyleSheet(COMBO_STYLE)
        tb.addWidget(self.filter_idea)

        lbl2 = QLabel("Ordenar:")
        lbl2.setStyleSheet("color: #666666; font-size: 13px; margin-left: 10px;")
        tb.addWidget(lbl2)

        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet(COMBO_STYLE)
        self.sort_combo.addItem("Fecha creación (reciente)", "fecha_desc")
        self.sort_combo.addItem("Fecha creación (antigua)", "fecha_asc")
        self.sort_combo.addItem("Nombre (A-Z)", "nombre")
        self.sort_combo.addItem("Estatus", "estatus")
        tb.addWidget(self.sort_combo)

        layout.addWidget(toolbar)

        # ── Table ────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "Proyecto / Idea", "Estatus",
            "Fecha Creación", "Último Cambio", "Acciones"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        hh2 = self.table.horizontalHeader()
        hh2.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh2.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh2.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh2.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh2.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hh2.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 224)
        self.table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.table)

        # ── Status bar ───────────────────────────────────────
        self.status_label = QLabel("0 tareas")
        self.status_label.setStyleSheet(
            "color: #888888; font-size: 12px; padding: 6px 24px;"
            "background: #FAFAFA; border-top: 1px solid #E0E0E0;"
        )
        layout.addWidget(self.status_label)

        # ── Signals ──────────────────────────────────────────
        self.btn_new.clicked.connect(self._open_new_form)
        self.search_input.textChanged.connect(self._apply_filters)
        self.filter_estatus.currentIndexChanged.connect(self._apply_filters)
        self.filter_idea.currentIndexChanged.connect(self._apply_filters)
        self.sort_combo.currentIndexChanged.connect(self._apply_filters)

        self.refresh()

    # ── Public ─────────────────────────────────────────────────────────────

    def refresh(self):
        self._all_tareas = load_all_tareas()
        self._rebuild_idea_filter()
        self._apply_filters()

    def refresh_for_idea(self, idea_id: str):
        """Called when an idea is saved to refresh task list."""
        self.refresh()

    # ── Private ────────────────────────────────────────────────────────────

    def _rebuild_idea_filter(self):
        current = self.filter_idea.currentData()
        self.filter_idea.blockSignals(True)
        self.filter_idea.clear()
        self.filter_idea.addItem("Todos los proyectos", None)
        self.filter_idea.addItem(IDEA_DEFAULT_NAME, IDEA_DEFAULT_ID)

        ideas_en_tareas = sorted(
            set((t.idea_id, t.idea_nombre) for t in self._all_tareas
                if t.idea_id != IDEA_DEFAULT_ID),
            key=lambda x: x[1].lower()
        )
        for iid, inombre in ideas_en_tareas:
            self.filter_idea.addItem(inombre, iid)

        for i in range(self.filter_idea.count()):
            if self.filter_idea.itemData(i) == current:
                self.filter_idea.setCurrentIndex(i)
                break
        self.filter_idea.blockSignals(False)

    def _apply_filters(self):
        tareas = list(self._all_tareas)
        search = self.search_input.text().strip().lower()
        estatus = self.filter_estatus.currentData()
        idea_id = self.filter_idea.currentData()
        sort_key = self.sort_combo.currentData()

        if search:
            tareas = [t for t in tareas if search in t.nombre.lower()]
        if estatus:
            tareas = [t for t in tareas if t.estatus == estatus]
        if idea_id:
            tareas = [t for t in tareas if t.idea_id == idea_id]

        STATUS_ORDER = {s: i for i, s in enumerate(TAREA_STATUS_LIST)}
        if sort_key == "fecha_desc":
            tareas.sort(key=lambda t: t.fecha_creacion, reverse=True)
        elif sort_key == "fecha_asc":
            tareas.sort(key=lambda t: t.fecha_creacion)
        elif sort_key == "nombre":
            tareas.sort(key=lambda t: t.nombre.lower())
        elif sort_key == "estatus":
            tareas.sort(key=lambda t: STATUS_ORDER.get(t.estatus, 9))

        self._populate_table(tareas)
        count, total = len(tareas), len(self._all_tareas)
        self.status_label.setText(
            f"{count} tarea{'s' if count != 1 else ''}"
            + (f" (de {total} total)" if count != total else "")
        )

    def _populate_table(self, tareas: List[Tarea]):
        self.table.setRowCount(0)
        for tarea in tareas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            item_nombre = QTableWidgetItem(tarea.nombre)
            item_nombre.setData(Qt.ItemDataRole.UserRole, tarea.id)
            self.table.setItem(row, 0, item_nombre)

            self.table.setItem(row, 1, QTableWidgetItem(tarea.idea_nombre))

            color = TAREA_STATUS_COLORS.get(tarea.estatus, "#888888")
            item_est = QTableWidgetItem(f"  {tarea.estatus}")
            item_est.setForeground(QBrush(QColor(color)))
            item_est.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.table.setItem(row, 2, item_est)

            self.table.setItem(row, 3, QTableWidgetItem(tarea.fecha_creacion_display()))
            self.table.setItem(row, 4, QTableWidgetItem(tarea.fecha_ultimo_cambio_display()))

            self.table.setCellWidget(row, 5, self._make_actions(tarea.id))

    def _make_actions(self, tarea_id: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(w)
        hl.setContentsMargins(10, 5, 10, 5)
        hl.setSpacing(14)

        btn_edit = QPushButton("✏  Editar")
        btn_edit.setStyleSheet(BTN_SECONDARY)
        btn_edit.setFixedSize(88, 32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(lambda: self._open_edit_form(tarea_id))

        btn_del = QPushButton("🗑  Borrar")
        btn_del.setStyleSheet(BTN_DANGER)
        btn_del.setFixedSize(96, 32)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda: self._confirm_delete(tarea_id))

        hl.addWidget(btn_edit)
        hl.addWidget(btn_del)
        return w

    def _open_new_form(self):
        from .tarea_form import TareaFormDialog
        dlg = TareaFormDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _open_edit_form(self, tarea_id: str):
        from .tarea_form import TareaFormDialog
        from ..data_manager import load_tarea
        tarea = load_tarea(tarea_id)
        if not tarea:
            QMessageBox.warning(self, "Error", "No se encontró la tarea.")
            return
        dlg = TareaFormDialog(tarea=tarea, parent=self)
        if dlg.exec():
            self.refresh()

    def _confirm_delete(self, tarea_id: str):
        from ..data_manager import load_tarea
        tarea = load_tarea(tarea_id)
        name = tarea.nombre if tarea else tarea_id
        reply = QMessageBox.question(
            self, "Eliminar Tarea",
            f"¿Estás seguro de que deseas eliminar la tarea:\n\n\"{name}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_tarea(tarea_id)
            self.refresh()
