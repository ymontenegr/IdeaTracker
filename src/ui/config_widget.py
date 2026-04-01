from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QLineEdit, QMessageBox, QFrame, QInputDialog,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..data_manager import (
    load_categories, add_category, edit_category,
    delete_category, get_ideas_count_by_category
)
from ..config import MAX_CATEGORIES


BTN_PRIMARY = """
QPushButton {
    background: #2196F3; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 9px 20px; font-size: 13px; font-weight: bold;
}
QPushButton:hover { background: #1976D2; }
QPushButton:disabled { background: #90CAF9; color: #FFFFFF; }
"""

BTN_EDIT = """
QPushButton {
    background: #FFFFFF; color: #333333; border: 1px solid #BBBBBB;
    border-radius: 6px; padding: 6px 16px; font-size: 12px;
    min-width: 70px;
}
QPushButton:hover { background: #F0F0F0; }
"""

BTN_DANGER = """
QPushButton {
    background: #E53935; color: #FFFFFF; border: none;
    border-radius: 6px; padding: 6px 16px; font-size: 12px;
    min-width: 80px;
}
QPushButton:hover { background: #C62828; }
"""


class ConfigWidget(QWidget):
    categories_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ─────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E0E0E0;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(24, 16, 24, 16)
        title = QLabel("Configuración")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A237E;")
        hh.addWidget(title)
        layout.addWidget(header)

        # ── Content ─────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background: #F5F7FA;")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(36, 28, 36, 28)
        cl.setSpacing(16)

        # Section header row
        sec_row = QHBoxLayout()
        sec_label = QLabel("Gestión de Categorías")
        sec_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
        sec_row.addWidget(sec_label)
        sec_row.addStretch()
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("font-size: 13px; color: #888888;")
        sec_row.addWidget(self.count_label)
        cl.addLayout(sec_row)

        # Add new category row
        add_row = QHBoxLayout()
        add_row.setSpacing(10)
        self.new_cat_input = QLineEdit()
        self.new_cat_input.setPlaceholderText("Nombre de la nueva categoría...")
        self.new_cat_input.setStyleSheet(
            "border: 1px solid #CCCCCC; border-radius: 6px; padding: 9px 12px; "
            "font-size: 13px; background: #FFFFFF; color: #333333;"
        )
        add_row.addWidget(self.new_cat_input)

        self.btn_add = QPushButton("+ Agregar Categoría")
        self.btn_add.setStyleSheet(BTN_PRIMARY)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setFixedHeight(40)
        add_row.addWidget(self.btn_add)
        cl.addLayout(add_row)

        # Scrollable list of categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; }"
        )

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: #FFFFFF;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()

        scroll.setWidget(self.list_container)
        cl.addWidget(scroll)

        # Tip
        tip = QLabel(
            "ℹ  Al editar el nombre de una categoría, todas las ideas asociadas se actualizarán automáticamente. "
            "Al eliminar una categoría, las ideas conservan el nombre anterior como referencia histórica."
        )
        tip.setStyleSheet("color: #999999; font-size: 12px; padding: 2px 0;")
        tip.setWordWrap(True)
        cl.addWidget(tip)

        layout.addWidget(content)

        # Signals
        self.btn_add.clicked.connect(self._add_category)
        self.new_cat_input.returnPressed.connect(self._add_category)

        self._refresh_list()

    # ── Helpers ────────────────────────────────────────────────────────────

    def _refresh_list(self):
        # Clear all rows except the trailing stretch
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cats = load_categories()
        count = len(cats)
        self.count_label.setText(f"{count} / {MAX_CATEGORIES} categorías")
        self.btn_add.setEnabled(count < MAX_CATEGORIES)

        for i, cat in enumerate(cats):
            row = self._make_row(cat.id, cat.nombre, i)
            self.list_layout.insertWidget(i, row)

    def _make_row(self, cat_id: str, nombre: str, index: int) -> QWidget:
        bg = "#FFFFFF" if index % 2 == 0 else "#F9FAFB"

        row = QWidget()
        row.setStyleSheet(f"background: {bg};")
        row.setFixedHeight(52)

        hl = QHBoxLayout(row)
        hl.setContentsMargins(18, 8, 18, 8)
        hl.setSpacing(12)

        # Category name
        lbl = QLabel(f"{index + 1}.  {nombre}")
        lbl.setStyleSheet("font-size: 14px; color: #222222; background: transparent;")
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hl.addWidget(lbl)

        btn_edit = QPushButton("✏  Editar")
        btn_edit.setStyleSheet(BTN_EDIT)
        btn_edit.setFixedSize(90, 34)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(lambda _=False, cid=cat_id, n=nombre: self._edit_category(cid, n))
        hl.addWidget(btn_edit)

        btn_del = QPushButton("🗑  Eliminar")
        btn_del.setStyleSheet(BTN_DANGER)
        btn_del.setFixedSize(100, 34)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda _=False, cid=cat_id, n=nombre: self._delete_category(cid, n))
        hl.addWidget(btn_del)

        return row

    def _add_category(self):
        nombre = self.new_cat_input.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo vacío", "Ingresa el nombre de la categoría.")
            return
        success, msg = add_category(nombre)
        if success:
            self.new_cat_input.clear()
            self._refresh_list()
            self.categories_changed.emit()
        else:
            QMessageBox.warning(self, "No se pudo agregar", msg)

    def _edit_category(self, cat_id: str, current_name: str):
        nuevo, ok = QInputDialog.getText(
            self, "Editar Categoría",
            f"Nuevo nombre para «{current_name}»:",
            text=current_name,
        )
        if not ok or not nuevo.strip():
            return
        success, msg = edit_category(cat_id, nuevo.strip())
        if success:
            self._refresh_list()
            self.categories_changed.emit()
            QMessageBox.information(self, "Categoría actualizada", msg)
        else:
            QMessageBox.warning(self, "Error", msg)

    def _delete_category(self, cat_id: str, nombre: str):
        count = get_ideas_count_by_category(cat_id)
        msg = f"¿Eliminar la categoría «{nombre}»?"
        if count > 0:
            msg += (
                f"\n\n⚠  Hay {count} idea{'s' if count != 1 else ''} asociada{'s' if count != 1 else ''} "
                f"a esta categoría. Las ideas NO serán eliminadas; conservarán el nombre de la "
                f"categoría como referencia histórica."
            )
        reply = QMessageBox.question(
            self, "Eliminar Categoría", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_category(cat_id)
            self._refresh_list()
            self.categories_changed.emit()
