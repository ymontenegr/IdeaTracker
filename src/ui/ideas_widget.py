from datetime import datetime
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QLineEdit, QMessageBox, QAbstractItemView, QFrame,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QBrush

from ..data_manager import load_all_ideas, load_categories, delete_idea
from ..models import Idea
from ..config import STATUS_COLORS, STATUS_LIST, PRIORIDADES, PRIORIDAD_COLORS


TOOLBAR_STYLE = """
QWidget#toolbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
}
"""

TABLE_STYLE = """
QTableWidget {
    background: #FFFFFF;
    color: #222222;
    border: none;
    gridline-color: #F0F0F0;
    font-size: 13px;
    selection-background-color: #E3F2FD;
    selection-color: #000000;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #F5F5F5;
    color: #222222;
}
QTableWidget::item:selected {
    background: #E3F2FD;
    color: #000000;
}
QHeaderView::section {
    background: #F8F9FA;
    color: #555555;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #E0E0E0;
    border-right: 1px solid #E8E8E8;
}
"""

BTN_PRIMARY = """
QPushButton {
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
QPushButton:pressed { background: #1565C0; }
"""

BTN_DANGER = """
QPushButton {
    background: #F44336;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover { background: #D32F2F; }
"""

BTN_SECONDARY = """
QPushButton {
    background: #FFFFFF;
    color: #333;
    border: 1px solid #CCC;
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
}
QPushButton:hover { background: #F5F5F5; }
"""

COMBO_STYLE = """
QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background: #FFFFFF;
    color: #222222;
    min-width: 130px;
}
QComboBox:!editable { color: #222222; }
QComboBox:!editable:on { color: #222222; }
QComboBox::drop-down { border: none; width: 20px; }
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

SEARCH_STYLE = """
QLineEdit {
    border: 1px solid #CCC;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    background: white;
    min-width: 200px;
}
"""


class IdeasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._all_ideas: List[Idea] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Ideas & Planes")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A237E;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.btn_new = QPushButton("+ Nueva Idea")
        self.btn_new.setStyleSheet(BTN_PRIMARY)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(self.btn_new)

        layout.addWidget(header)

        # ── Filters toolbar ─────────────────────────────────
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setStyleSheet(TOOLBAR_STYLE)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(24, 10, 24, 10)
        tb_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por nombre...")
        self.search_input.setStyleSheet(SEARCH_STYLE)
        tb_layout.addWidget(self.search_input)

        tb_layout.addStretch()

        lbl_filter = QLabel("Filtrar:")
        lbl_filter.setStyleSheet("color: #666; font-size: 13px;")
        tb_layout.addWidget(lbl_filter)

        self.filter_cat = QComboBox()
        self.filter_cat.setStyleSheet(COMBO_STYLE)
        self.filter_cat.addItem("Todas las categorías", None)
        tb_layout.addWidget(self.filter_cat)

        self.filter_prioridad = QComboBox()
        self.filter_prioridad.setStyleSheet(COMBO_STYLE)
        self.filter_prioridad.addItem("Todas las prioridades", None)
        for p in PRIORIDADES:
            self.filter_prioridad.addItem(p, p)
        tb_layout.addWidget(self.filter_prioridad)

        self.filter_estatus = QComboBox()
        self.filter_estatus.setStyleSheet(COMBO_STYLE)
        self.filter_estatus.addItem("Todos los estatus", None)
        for s in STATUS_LIST:
            self.filter_estatus.addItem(s, s)
        tb_layout.addWidget(self.filter_estatus)

        self.filter_mes = QComboBox()
        self.filter_mes.setStyleSheet(COMBO_STYLE)
        self.filter_mes.addItem("Todos los meses", None)
        tb_layout.addWidget(self.filter_mes)

        lbl_sort = QLabel("Ordenar:")
        lbl_sort.setStyleSheet("color: #666; font-size: 13px; margin-left: 10px;")
        tb_layout.addWidget(lbl_sort)

        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet(COMBO_STYLE)
        self.sort_combo.addItem("Fecha (más reciente)", "fecha_desc")
        self.sort_combo.addItem("Fecha (más antigua)", "fecha_asc")
        self.sort_combo.addItem("Prioridad", "prioridad")
        self.sort_combo.addItem("Nombre (A-Z)", "nombre")
        tb_layout.addWidget(self.sort_combo)

        layout.addWidget(toolbar)

        # ── Table ────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "Categoría", "Prioridad", "Estatus",
            "Fecha Registro", "Fecha Inicio", "Acciones"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(TABLE_STYLE + "QTableWidget { alternate-background-color: #FAFAFA; }")

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 224)
        self.table.setRowHeight(0, 48)
        self.table.verticalHeader().setDefaultSectionSize(48)

        layout.addWidget(self.table)

        # ── Status bar ───────────────────────────────────────
        self.status_label = QLabel("0 ideas")
        self.status_label.setStyleSheet(
            "color: #888; font-size: 12px; padding: 6px 24px;"
            "background: #FAFAFA; border-top: 1px solid #E0E0E0;"
        )
        layout.addWidget(self.status_label)

        # ── Signals ─────────────────────────────────────────
        self.btn_new.clicked.connect(self._open_new_form)
        self.search_input.textChanged.connect(self._apply_filters)
        self.filter_cat.currentIndexChanged.connect(self._apply_filters)
        self.filter_prioridad.currentIndexChanged.connect(self._apply_filters)
        self.filter_estatus.currentIndexChanged.connect(self._apply_filters)
        self.filter_mes.currentIndexChanged.connect(self._apply_filters)
        self.sort_combo.currentIndexChanged.connect(self._apply_filters)

        self.refresh()

    # ── Public ─────────────────────────────────────────────────────────────

    def refresh(self):
        self._all_ideas = load_all_ideas()
        self._rebuild_month_filter()
        self._apply_filters()

    def refresh_categories(self):
        current = self.filter_cat.currentData()
        self.filter_cat.blockSignals(True)
        self.filter_cat.clear()
        self.filter_cat.addItem("Todas las categorías", None)
        for cat in load_categories():
            self.filter_cat.addItem(cat.nombre, cat.id)
        # Restore selection if still available
        for i in range(self.filter_cat.count()):
            if self.filter_cat.itemData(i) == current:
                self.filter_cat.setCurrentIndex(i)
                break
        self.filter_cat.blockSignals(False)
        self._apply_filters()

    # ── Private ────────────────────────────────────────────────────────────

    def _rebuild_month_filter(self):
        current = self.filter_mes.currentData()
        self.filter_mes.blockSignals(True)
        self.filter_mes.clear()
        self.filter_mes.addItem("Todos los meses", None)

        months = sorted(set(i.mes_registro() for i in self._all_ideas), reverse=True)
        for year, month in months:
            if year == 0:
                continue
            label = datetime(year, month, 1).strftime("%B %Y").capitalize()
            self.filter_mes.addItem(label, (year, month))

        for i in range(self.filter_mes.count()):
            if self.filter_mes.itemData(i) == current:
                self.filter_mes.setCurrentIndex(i)
                break
        self.filter_mes.blockSignals(False)

        # Also refresh categories combo
        self.refresh_categories()

    def _apply_filters(self):
        ideas = list(self._all_ideas)
        search = self.search_input.text().strip().lower()
        cat_id = self.filter_cat.currentData()
        prioridad = self.filter_prioridad.currentData()
        estatus = self.filter_estatus.currentData()
        mes = self.filter_mes.currentData()
        sort_key = self.sort_combo.currentData()

        if search:
            ideas = [i for i in ideas if search in i.nombre.lower()]
        if cat_id:
            ideas = [i for i in ideas if i.categoria_id == cat_id]
        if prioridad:
            ideas = [i for i in ideas if i.prioridad == prioridad]
        if estatus:
            ideas = [i for i in ideas if i.estatus == estatus]
        if mes:
            ideas = [i for i in ideas if i.mes_registro() == mes]

        PRIORIDAD_ORDER = {"Alta": 0, "Media": 1, "Baja": 2}
        if sort_key == "fecha_desc":
            ideas.sort(key=lambda i: i.fecha_registro, reverse=True)
        elif sort_key == "fecha_asc":
            ideas.sort(key=lambda i: i.fecha_registro)
        elif sort_key == "prioridad":
            ideas.sort(key=lambda i: PRIORIDAD_ORDER.get(i.prioridad, 9))
        elif sort_key == "nombre":
            ideas.sort(key=lambda i: i.nombre.lower())

        self._populate_table(ideas)
        count = len(ideas)
        total = len(self._all_ideas)
        self.status_label.setText(
            f"{count} idea{'s' if count != 1 else ''}"
            + (f" (de {total} total)" if count != total else "")
        )

    def _populate_table(self, ideas: List[Idea]):
        self.table.setRowCount(0)
        for idea in ideas:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Nombre
            item_nombre = QTableWidgetItem(idea.nombre)
            item_nombre.setData(Qt.ItemDataRole.UserRole, idea.id)
            self.table.setItem(row, 0, item_nombre)

            # Categoría
            self.table.setItem(row, 1, QTableWidgetItem(idea.categoria_nombre))

            # Prioridad
            item_prio = QTableWidgetItem(idea.prioridad)
            color = PRIORIDAD_COLORS.get(idea.prioridad, "#888")
            item_prio.setForeground(QBrush(QColor(color)))
            item_prio.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.table.setItem(row, 2, item_prio)

            # Estatus
            status_color = STATUS_COLORS.get(idea.estatus, "#888")
            item_status = QTableWidgetItem(f"  {idea.estatus}")
            item_status.setForeground(QBrush(QColor(status_color)))
            item_status.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.table.setItem(row, 3, item_status)

            # Fecha Registro
            self.table.setItem(row, 4, QTableWidgetItem(idea.fecha_registro_display()))

            # Fecha Inicio
            self.table.setItem(row, 5, QTableWidgetItem(idea.fecha_inicio_display()))

            # Acciones
            actions_widget = self._make_actions_widget(idea.id)
            self.table.setCellWidget(row, 6, actions_widget)

    def _make_actions_widget(self, idea_id: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(w)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(14)

        btn_edit = QPushButton("✏  Editar")
        btn_edit.setStyleSheet(BTN_SECONDARY)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setFixedSize(88, 32)

        btn_del = QPushButton("🗑  Borrar")
        btn_del.setStyleSheet(BTN_DANGER)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFixedSize(96, 32)

        btn_edit.clicked.connect(lambda: self._open_edit_form(idea_id))
        btn_del.clicked.connect(lambda: self._confirm_delete(idea_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        return w

    def _open_new_form(self):
        from .idea_form import IdeaFormDialog
        dlg = IdeaFormDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _open_edit_form(self, idea_id: str):
        from ..data_manager import load_idea
        from .idea_form import IdeaFormDialog
        idea = load_idea(idea_id)
        if idea is None:
            QMessageBox.warning(self, "Error", "No se encontró la idea.")
            return
        dlg = IdeaFormDialog(idea=idea, parent=self)
        if dlg.exec():
            self.refresh()

    def _confirm_delete(self, idea_id: str):
        from ..data_manager import load_idea
        idea = load_idea(idea_id)
        name = idea.nombre if idea else idea_id
        reply = QMessageBox.question(
            self, "Eliminar Idea",
            f"¿Estás seguro de que deseas eliminar la idea:\n\n\"{name}\"?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_idea(idea_id)
            self.refresh()
