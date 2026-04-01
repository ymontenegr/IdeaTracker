from datetime import datetime, date
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QDateEdit, QDoubleSpinBox, QScrollArea, QWidget,
    QFrame, QMessageBox, QSizePolicy, QListWidget,
    QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from ..data_manager import load_categories, create_idea, save_idea, add_nota
from ..models import Idea
from ..config import STATUS_LIST, STATUS_COLORS, PRIORIDADES, ORIGENES_DEFAULT


FORM_STYLE = """
QDialog {
    background: #F5F7FA;
}
QLabel.section-title {
    font-size: 13px;
    font-weight: bold;
    color: #1A237E;
    padding: 6px 0 2px 0;
}
QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QDateEdit {
    border: 1px solid #CCC;
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    background: #FFFFFF;
    color: #222222;
}
QComboBox:!editable { color: #222222; }
QComboBox:!editable:on { color: #222222; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QDoubleSpinBox:focus, QDateEdit:focus {
    border-color: #2196F3;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background: #FFFFFF; color: #222222;
    selection-background-color: #E3F2FD;
    selection-color: #000000;
}
"""

BTN_PRIMARY = """
QPushButton {
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
"""

BTN_SECONDARY = """
QPushButton {
    background: #FFFFFF;
    color: #333;
    border: 1px solid #CCC;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: 14px;
}
QPushButton:hover { background: #F5F5F5; }
"""

BTN_ADD_NOTE = """
QPushButton {
    background: #E8F5E9;
    color: #2E7D32;
    border: 1px solid #A5D6A7;
    border-radius: 6px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton:hover { background: #C8E6C9; }
"""


def _section_title(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #1A237E; margin-top: 8px;")
    return lbl


def _separator() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color: #E0E0E0;")
    return f


class IdeaFormDialog(QDialog):
    def __init__(self, idea: Optional[Idea] = None, parent=None):
        super().__init__(parent)
        self._idea = idea
        self._is_edit = idea is not None
        self.setWindowTitle("Editar Idea" if self._is_edit else "Nueva Idea")
        self.setMinimumSize(760, 650)
        self.resize(820, 720)
        self.setStyleSheet(FORM_STYLE)
        self._build_ui()
        if self._is_edit:
            self._populate_fields()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A237E;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 16, 24, 16)
        title_lbl = QLabel("Editar Idea" if self._is_edit else "Registrar Nueva Idea")
        title_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        hh.addWidget(title_lbl)
        root.addWidget(header)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F5F7FA; border: none; }")

        body = QWidget()
        body.setStyleSheet("background: #F5F7FA;")
        form_layout = QVBoxLayout(body)
        form_layout.setContentsMargins(28, 20, 28, 20)
        form_layout.setSpacing(10)

        # ── Basic Info ──────────────────────────────────────
        form_layout.addWidget(_section_title("Información General"))

        fl1 = QFormLayout()
        fl1.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl1.setHorizontalSpacing(16)
        fl1.setVerticalSpacing(10)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Título de la idea...")
        fl1.addRow("Nombre / Tema *", self.nombre_input)

        self.descripcion_input = QTextEdit()
        self.descripcion_input.setPlaceholderText("Descripción detallada del plan o idea...")
        self.descripcion_input.setMinimumHeight(90)
        fl1.addRow("Descripción *", self.descripcion_input)

        self.origen_combo = QComboBox()
        self.origen_combo.setEditable(True)
        self.origen_combo.addItems(ORIGENES_DEFAULT)
        self.origen_combo.setPlaceholderText("Selecciona o escribe el origen...")
        fl1.addRow("Origen de la Idea *", self.origen_combo)

        form_layout.addLayout(fl1)
        form_layout.addWidget(_separator())

        # ── Dates / Cost ────────────────────────────────────
        form_layout.addWidget(_section_title("Fechas y Costos"))

        fl2 = QFormLayout()
        fl2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl2.setHorizontalSpacing(16)
        fl2.setVerticalSpacing(10)

        if self._is_edit and self._idea:
            try:
                dt = datetime.fromisoformat(self._idea.fecha_registro)
                fecha_reg_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                fecha_reg_str = self._idea.fecha_registro
            lbl_fecha_reg = QLabel(fecha_reg_str)
            lbl_fecha_reg.setStyleSheet("font-size: 13px; color: #555; padding: 7px 0;")
            fl2.addRow("Fecha de Registro", lbl_fecha_reg)
        else:
            lbl_fecha_reg = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M") + "  (automática)")
            lbl_fecha_reg.setStyleSheet("font-size: 13px; color: #888; padding: 7px 0;")
            fl2.addRow("Fecha de Registro", lbl_fecha_reg)

        self.fecha_inicio_input = QDateEdit()
        self.fecha_inicio_input.setCalendarPopup(True)
        self.fecha_inicio_input.setDisplayFormat("dd/MM/yyyy")
        self.fecha_inicio_input.setDate(QDate.currentDate())
        fl2.addRow("Fecha Probable de Inicio *", self.fecha_inicio_input)

        self.costo_input = QDoubleSpinBox()
        self.costo_input.setPrefix("$ ")
        self.costo_input.setMaximum(999_999_999)
        self.costo_input.setDecimals(2)
        self.costo_input.setSingleStep(100)
        fl2.addRow("Costo Aproximado *", self.costo_input)

        self.beneficio_input = QTextEdit()
        self.beneficio_input.setPlaceholderText("Describe el retorno o valor esperado...")
        self.beneficio_input.setMinimumHeight(70)
        fl2.addRow("Beneficio Esperado *", self.beneficio_input)

        form_layout.addLayout(fl2)
        form_layout.addWidget(_separator())

        # ── Classification ──────────────────────────────────
        form_layout.addWidget(_section_title("Clasificación"))

        fl3 = QFormLayout()
        fl3.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        fl3.setHorizontalSpacing(16)
        fl3.setVerticalSpacing(10)

        self.categoria_combo = QComboBox()
        self._load_categories()
        fl3.addRow("Categoría *", self.categoria_combo)

        self.prioridad_combo = QComboBox()
        for p in PRIORIDADES:
            self.prioridad_combo.addItem(p, p)
        fl3.addRow("Prioridad *", self.prioridad_combo)

        if self._is_edit:
            self.estatus_combo = QComboBox()
            for s in STATUS_LIST:
                self.estatus_combo.addItem(s, s)
            self._update_estatus_style()
            self.estatus_combo.currentIndexChanged.connect(self._update_estatus_style)
            fl3.addRow("Estatus", self.estatus_combo)

        form_layout.addLayout(fl3)
        form_layout.addWidget(_separator())

        # ── Notes (edit mode only) ─────────────────────────
        if self._is_edit:
            form_layout.addWidget(_section_title("Notas / Observaciones"))

            self.notes_list = QListWidget()
            self.notes_list.setStyleSheet("""
                QListWidget {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    background: white;
                    font-size: 12px;
                }
                QListWidget::item {
                    padding: 8px 10px;
                    border-bottom: 1px solid #F0F0F0;
                }
            """)
            self.notes_list.setMinimumHeight(120)
            self.notes_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection
                                              if hasattr(QAbstractItemView, 'SelectionMode')
                                              else self.notes_list.setSelectionMode)
            form_layout.addWidget(self.notes_list)

            note_row = QHBoxLayout()
            self.note_input = QLineEdit()
            self.note_input.setPlaceholderText("Escribe una nueva nota...")
            note_row.addWidget(self.note_input)

            btn_add_note = QPushButton("+ Agregar nota")
            btn_add_note.setStyleSheet(BTN_ADD_NOTE)
            btn_add_note.clicked.connect(self._add_note)
            note_row.addWidget(btn_add_note)
            form_layout.addLayout(note_row)

            self._populate_notes()

        form_layout.addStretch()
        scroll.setWidget(body)
        root.addWidget(scroll)

        # Footer buttons
        footer = QWidget()
        footer.setStyleSheet("background: #FFFFFF; border-top: 1px solid #E0E0E0;")
        foot_layout = QHBoxLayout(footer)
        foot_layout.setContentsMargins(24, 14, 24, 14)
        foot_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(BTN_SECONDARY)
        btn_cancel.clicked.connect(self.reject)
        foot_layout.addWidget(btn_cancel)

        btn_save = QPushButton("💾  Guardar")
        btn_save.setStyleSheet(BTN_PRIMARY)
        btn_save.clicked.connect(self._save)
        foot_layout.addWidget(btn_save)

        root.addWidget(footer)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _load_categories(self):
        self.categoria_combo.clear()
        for cat in load_categories():
            self.categoria_combo.addItem(cat.nombre, cat.id)

    def _populate_fields(self):
        idea = self._idea
        self.nombre_input.setText(idea.nombre)
        self.descripcion_input.setPlainText(idea.descripcion)

        # Origen
        idx = self.origen_combo.findText(idea.origen)
        if idx >= 0:
            self.origen_combo.setCurrentIndex(idx)
        else:
            self.origen_combo.setEditText(idea.origen)

        # Fecha inicio
        try:
            d = date.fromisoformat(idea.fecha_inicio_probable)
            self.fecha_inicio_input.setDate(QDate(d.year, d.month, d.day))
        except Exception:
            pass

        self.costo_input.setValue(idea.costo_aproximado)
        self.beneficio_input.setPlainText(idea.beneficio_esperado)

        # Categoria
        for i in range(self.categoria_combo.count()):
            if self.categoria_combo.itemData(i) == idea.categoria_id:
                self.categoria_combo.setCurrentIndex(i)
                break
        else:
            # Category was deleted; show stored name
            self.categoria_combo.addItem(f"{idea.categoria_nombre} (eliminada)", idea.categoria_id)
            self.categoria_combo.setCurrentIndex(self.categoria_combo.count() - 1)

        # Prioridad
        idx_p = self.prioridad_combo.findData(idea.prioridad)
        if idx_p >= 0:
            self.prioridad_combo.setCurrentIndex(idx_p)

        # Estatus
        idx_e = self.estatus_combo.findData(idea.estatus)
        if idx_e >= 0:
            self.estatus_combo.setCurrentIndex(idx_e)

    def _populate_notes(self):
        self.notes_list.clear()
        if self._idea:
            for nota in reversed(self._idea.notas):
                item = QListWidgetItem(f"[{nota.fecha_display()}]  {nota.texto}")
                self.notes_list.addItem(item)

    def _update_estatus_style(self):
        if not hasattr(self, 'estatus_combo'):
            return
        estatus = self.estatus_combo.currentData()
        color = STATUS_COLORS.get(estatus, "#888")
        self.estatus_combo.setStyleSheet(
            f"QComboBox {{ border: 2px solid {color}; border-radius: 6px; "
            f"padding: 7px 10px; font-size: 13px; font-weight: bold; "
            f"color: {color}; background: white; }}"
            "QComboBox::drop-down { border: none; width: 24px; }"
            "QComboBox QAbstractItemView { border: 1px solid #CCC; "
            "selection-background-color: #E3F2FD; }"
        )

    def _add_note(self):
        if not self._idea:
            return
        text = self.note_input.text().strip()
        if not text:
            QMessageBox.warning(self, "Nota vacía", "Escribe el texto de la nota antes de agregar.")
            return
        updated = add_nota(self._idea.id, text)
        if updated:
            self._idea = updated
            self._populate_notes()
            self.note_input.clear()

    # ── Save ───────────────────────────────────────────────────────────────

    def _save(self):
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        origen = self.origen_combo.currentText().strip()
        beneficio = self.beneficio_input.toPlainText().strip()

        errors = []
        if not nombre:
            errors.append("• Nombre / Tema es obligatorio.")
        if not descripcion:
            errors.append("• Descripción general es obligatoria.")
        if not origen:
            errors.append("• Origen de la idea es obligatorio.")
        if not beneficio:
            errors.append("• Beneficio esperado es obligatorio.")
        if self.categoria_combo.count() == 0:
            errors.append("• Debe existir al menos una categoría.")

        if errors:
            QMessageBox.warning(self, "Campos requeridos", "\n".join(errors))
            return

        cat_id = self.categoria_combo.currentData()
        cat_nombre = self.categoria_combo.currentText()
        prioridad = self.prioridad_combo.currentData()
        costo = self.costo_input.value()
        q_date = self.fecha_inicio_input.date()
        fecha_inicio = f"{q_date.year():04d}-{q_date.month():02d}-{q_date.day():02d}"

        if self._is_edit and self._idea:
            idea = self._idea
            idea.nombre = nombre
            idea.descripcion = descripcion
            idea.origen = origen
            idea.fecha_inicio_probable = fecha_inicio
            idea.costo_aproximado = costo
            idea.beneficio_esperado = beneficio
            idea.categoria_id = cat_id
            idea.categoria_nombre = cat_nombre
            idea.prioridad = prioridad
            idea.estatus = self.estatus_combo.currentData()
            save_idea(idea)
        else:
            create_idea(
                nombre=nombre,
                descripcion=descripcion,
                origen=origen,
                fecha_inicio_probable=fecha_inicio,
                costo_aproximado=costo,
                beneficio_esperado=beneficio,
                categoria_id=cat_id or "",
                categoria_nombre=cat_nombre,
                prioridad=prioridad,
            )

        self.accept()


# Fix missing import
from PyQt6.QtWidgets import QAbstractItemView
