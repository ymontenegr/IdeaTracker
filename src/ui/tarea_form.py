from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QScrollArea, QWidget, QFrame, QMessageBox, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt

from ..data_manager import (
    load_all_ideas, create_tarea, save_tarea,
    cambiar_estatus_tarea, load_tarea
)
from ..models import Tarea
from ..config import (
    TAREA_STATUS_LIST, TAREA_STATUS_COLORS,
    IDEA_DEFAULT_ID, IDEA_DEFAULT_NAME
)


FORM_STYLE = """
QDialog { background: #F5F7FA; }
QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #CCCCCC; border-radius: 6px;
    padding: 7px 10px; font-size: 13px;
    background: #FFFFFF; color: #222222;
}
QComboBox:!editable { color: #222222; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC; background: #FFFFFF; color: #222222;
    selection-background-color: #E3F2FD; selection-color: #000000;
}
"""

BTN_PRIMARY = """
QPushButton {
    background: #2196F3; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
"""

BTN_SECONDARY = """
QPushButton {
    background: #FFFFFF; color: #333333; border: 1px solid #CCCCCC;
    border-radius: 6px; padding: 10px 24px; font-size: 14px;
}
QPushButton:hover { background: #F5F5F5; }
"""


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color: #E0E0E0;")
    return f


def _section(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1A237E; margin-top: 8px;")
    return lbl


class TareaFormDialog(QDialog):
    def __init__(self, tarea: Optional[Tarea] = None,
                 idea_id: Optional[str] = None,
                 idea_nombre: Optional[str] = None,
                 parent=None):
        super().__init__(parent)
        self._tarea = tarea
        self._is_edit = tarea is not None
        # Pre-selected idea (when opened from idea form)
        self._preset_idea_id = idea_id
        self._preset_idea_nombre = idea_nombre
        self.setWindowTitle("Editar Tarea" if self._is_edit else "Nueva Tarea")
        self.setMinimumSize(640, 520)
        self.resize(700, 580)
        self.setStyleSheet(FORM_STYLE)
        self._build_ui()
        if self._is_edit:
            self._populate_fields()
        elif self._preset_idea_id:
            self._preset_idea()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A237E;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 16, 24, 16)
        title_lbl = QLabel("Editar Tarea" if self._is_edit else "Registrar Nueva Tarea")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")
        hh.addWidget(title_lbl)
        root.addWidget(header)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F5F7FA; border: none; }")

        body = QWidget()
        body.setStyleSheet("background: #F5F7FA;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(28, 20, 28, 20)
        bl.setSpacing(10)

        # ── Fields ────────────────────────────────────────
        bl.addWidget(_section("Información de la Tarea"))

        fl = QFormLayout()
        fl.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl.setHorizontalSpacing(16)
        fl.setVerticalSpacing(10)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre de la tarea...")
        fl.addRow("Nombre *", self.nombre_input)

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada de la tarea...")
        self.descripcion_input.setMinimumHeight(90)
        fl.addRow("Descripción", self.descripcion_input)

        bl.addLayout(fl)
        bl.addWidget(_sep())

        # ── Proyecto / Idea ────────────────────────────────
        bl.addWidget(_section("Proyecto Asociado"))

        fl2 = QFormLayout()
        fl2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl2.setHorizontalSpacing(16)
        fl2.setVerticalSpacing(10)

        self.idea_combo = QComboBox()
        self.idea_combo.addItem(IDEA_DEFAULT_NAME, IDEA_DEFAULT_ID)
        ideas = sorted(load_all_ideas(), key=lambda i: i.nombre.lower())
        for idea in ideas:
            self.idea_combo.addItem(idea.nombre, idea.id)
        fl2.addRow("Proyecto / Idea", self.idea_combo)

        # Fecha de creación (read-only in edit)
        if self._is_edit and self._tarea:
            lbl_fecha = QLabel(self._tarea.fecha_creacion_display())
            lbl_fecha.setStyleSheet("font-size: 13px; color: #555555; padding: 7px 0;")
            fl2.addRow("Fecha de Creación", lbl_fecha)

        bl.addLayout(fl2)
        bl.addWidget(_sep())

        # ── Estatus (edit mode only) ───────────────────────
        if self._is_edit:
            bl.addWidget(_section("Estatus"))

            fl3 = QFormLayout()
            fl3.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            fl3.setHorizontalSpacing(16)
            fl3.setVerticalSpacing(10)

            self.estatus_combo = QComboBox()
            for s in TAREA_STATUS_LIST:
                self.estatus_combo.addItem(s, s)
            self.estatus_combo.currentIndexChanged.connect(self._update_estatus_style)
            fl3.addRow("Estatus", self.estatus_combo)
            bl.addLayout(fl3)
            bl.addWidget(_sep())

            # ── Status history ─────────────────────────────
            bl.addWidget(_section("Historial de Estatus"))
            self.historial_list = QListWidget()
            self.historial_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #E0E0E0; border-radius: 6px;
                    background: #FFFFFF; font-size: 12px; color: #222222;
                }
                QListWidget::item { padding: 7px 10px; border-bottom: 1px solid #F0F0F0; color: #222222; }
            """)
            self.historial_list.setMinimumHeight(100)
            self.historial_list.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection
            )
            bl.addWidget(self.historial_list)

        bl.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background: #FFFFFF; border-top: 1px solid #E0E0E0;")
        fl_foot = QHBoxLayout(footer)
        fl_foot.setContentsMargins(24, 14, 24, 14)
        fl_foot.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(BTN_SECONDARY)
        btn_cancel.clicked.connect(self.reject)
        fl_foot.addWidget(btn_cancel)

        btn_save = QPushButton("💾  Guardar")
        btn_save.setStyleSheet(BTN_PRIMARY)
        btn_save.clicked.connect(self._save)
        fl_foot.addWidget(btn_save)

        root.addWidget(footer)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _populate_fields(self):
        t = self._tarea
        self.nombre_input.setText(t.nombre)
        self.descripcion_input.setPlainText(t.descripcion)

        for i in range(self.idea_combo.count()):
            if self.idea_combo.itemData(i) == t.idea_id:
                self.idea_combo.setCurrentIndex(i)
                break

        idx = self.estatus_combo.findData(t.estatus)
        if idx >= 0:
            self.estatus_combo.setCurrentIndex(idx)
        self._update_estatus_style()
        self._populate_historial()

    def _preset_idea(self):
        for i in range(self.idea_combo.count()):
            if self.idea_combo.itemData(i) == self._preset_idea_id:
                self.idea_combo.setCurrentIndex(i)
                return

    def _populate_historial(self):
        self.historial_list.clear()
        if self._tarea:
            for h in reversed(self._tarea.historial_estatus):
                color = TAREA_STATUS_COLORS.get(h.estatus, "#888888")
                item = QListWidgetItem(f"[{h.fecha_display()}]  →  {h.estatus}")
                self.historial_list.addItem(item)

    def _update_estatus_style(self):
        if not hasattr(self, 'estatus_combo'):
            return
        estatus = self.estatus_combo.currentData()
        color = TAREA_STATUS_COLORS.get(estatus, "#888888")
        self.estatus_combo.setStyleSheet(
            f"QComboBox {{ border: 2px solid {color}; border-radius: 6px; "
            f"padding: 7px 10px; font-size: 13px; font-weight: bold; "
            f"color: {color}; background: #FFFFFF; }}"
            "QComboBox:!editable { color: " + color + "; }"
            "QComboBox::drop-down { border: none; width: 24px; }"
            "QComboBox QAbstractItemView { border: 1px solid #CCCCCC; "
            "background: #FFFFFF; color: #222222; "
            "selection-background-color: #E3F2FD; }"
        )

    def _save(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo requerido", "El nombre de la tarea es obligatorio.")
            return

        descripcion = self.descripcion_input.toPlainText().strip()
        idea_id = self.idea_combo.currentData() or IDEA_DEFAULT_ID
        idea_nombre = self.idea_combo.currentText()

        if self._is_edit and self._tarea:
            self._tarea.nombre = nombre
            self._tarea.descripcion = descripcion
            self._tarea.idea_id = idea_id
            self._tarea.idea_nombre = idea_nombre
            nuevo_estatus = self.estatus_combo.currentData()
            if nuevo_estatus != self._tarea.estatus:
                cambiar_estatus_tarea(self._tarea.id, nuevo_estatus)
                # Reload to get updated historial
                updated = load_tarea(self._tarea.id)
                if updated:
                    updated.nombre = nombre
                    updated.descripcion = descripcion
                    updated.idea_id = idea_id
                    updated.idea_nombre = idea_nombre
                    save_tarea(updated)
            else:
                save_tarea(self._tarea)
        else:
            create_tarea(
                nombre=nombre,
                descripcion=descripcion,
                idea_id=idea_id,
                idea_nombre=idea_nombre,
            )

        self.accept()


# Fix missing import
from PyQt6.QtWidgets import QAbstractItemView
