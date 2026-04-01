import os
import tempfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QWidget, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage

from ..config import EXPORTS_DIR


BTN_DOWNLOAD = """
QPushButton {
    background: #4CAF50; color: white; border: none;
    border-radius: 6px; padding: 10px 24px; font-size: 14px; font-weight: bold;
}
QPushButton:hover { background: #388E3C; }
"""

BTN_CLOSE = """
QPushButton {
    background: #FFFFFF; color: #333; border: 1px solid #CCC;
    border-radius: 6px; padding: 10px 24px; font-size: 14px;
}
QPushButton:hover { background: #F5F5F5; }
"""


class PDFPreviewDialog(QDialog):
    """
    Shows a PDF preview using rendered page images (via pdf2image / poppler).
    Falls back to a plain text notice if rendering is unavailable.
    """

    def __init__(self, pdf_bytes: bytes, suggested_name: str, parent=None):
        super().__init__(parent)
        self._pdf_bytes = pdf_bytes
        self._suggested_name = suggested_name
        self.setWindowTitle("Vista Previa del Reporte")
        self.setMinimumSize(820, 680)
        self.resize(900, 740)
        self._build_ui()
        self._load_preview()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("background: #1A237E;")
        hh = QHBoxLayout(header)
        hh.setContentsMargins(20, 12, 20, 12)
        lbl = QLabel("Vista Previa — Reporte")
        lbl.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        hh.addWidget(lbl)
        layout.addWidget(header)

        # Scroll area for content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("QScrollArea { background: #E0E0E0; }")

        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background: #E0E0E0;")
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(20, 20, 20, 20)
        self.preview_layout.setSpacing(12)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.scroll.setWidget(self.preview_container)
        layout.addWidget(self.scroll)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background: white; border-top: 1px solid #E0E0E0;")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 12, 20, 12)
        fl.addStretch()

        btn_close = QPushButton("Cerrar")
        btn_close.setStyleSheet(BTN_CLOSE)
        btn_close.clicked.connect(self.reject)
        fl.addWidget(btn_close)

        btn_download = QPushButton("⬇  Descargar PDF")
        btn_download.setStyleSheet(BTN_DOWNLOAD)
        btn_download.clicked.connect(self._download_pdf)
        fl.addWidget(btn_download)

        layout.addWidget(footer)

    def _load_preview(self):
        """Try to render PDF pages; fall back to message if not possible."""
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(self._pdf_bytes, dpi=130, fmt="ppm")
            for img in images:
                # Convert PIL image to QPixmap
                img_rgb = img.convert("RGB")
                data = img_rgb.tobytes("raw", "RGB")
                qimg = QImage(
                    data, img_rgb.width, img_rgb.height,
                    img_rgb.width * 3, QImage.Format.Format_RGB888
                )
                pixmap = QPixmap.fromImage(qimg)
                page_lbl = QLabel()
                page_lbl.setPixmap(pixmap)
                page_lbl.setStyleSheet(
                    "background: white; border: 1px solid #BDBDBD; "
                    "box-shadow: 2px 2px 6px rgba(0,0,0,0.2);"
                )
                page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.preview_layout.addWidget(page_lbl)
        except ImportError:
            self._show_fallback()
        except Exception as e:
            self._show_fallback(str(e))

    def _show_fallback(self, detail: str = ""):
        msg_widget = QWidget()
        msg_widget.setStyleSheet(
            "background: white; border-radius: 10px; "
            "border: 1px solid #E0E0E0;"
        )
        ml = QVBoxLayout(msg_widget)
        ml.setContentsMargins(40, 40, 40, 40)
        ml.setSpacing(12)

        icon_lbl = QLabel("📄")
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ml.addWidget(icon_lbl)

        title_lbl = QLabel("Reporte generado exitosamente")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1A237E;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ml.addWidget(title_lbl)

        sub_lbl = QLabel(
            "El reporte está listo para descargarse.\n"
            "Para ver la vista previa en pantalla instala poppler-utils:\n"
            "  sudo apt install poppler-utils\n"
            "  pip install pdf2image"
        )
        sub_lbl.setStyleSheet("font-size: 13px; color: #666;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_lbl.setWordWrap(True)
        ml.addWidget(sub_lbl)

        if detail:
            detail_lbl = QLabel(f"Detalle técnico: {detail}")
            detail_lbl.setStyleSheet("font-size: 11px; color: #AAA;")
            detail_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_lbl.setWordWrap(True)
            ml.addWidget(detail_lbl)

        self.preview_layout.addWidget(msg_widget)

    def _download_pdf(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._suggested_name}_{timestamp}.pdf"
        dest = EXPORTS_DIR / filename
        try:
            with open(dest, "wb") as f:
                f.write(self._pdf_bytes)
            QMessageBox.information(
                self, "PDF Guardado",
                f"El reporte se guardó en:\n{dest}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))
