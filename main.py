#!/usr/bin/env python3
"""
IdeaTracker — Entry point
Desktop application for managing ideas and business plans.
"""

import sys
import os

# Ensure the project directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from src.config import setup_directories
from src.ui.main_window import MainWindow


def main():
    setup_directories()

    app = QApplication(sys.argv)
    app.setApplicationName("ideaTracker")        # debe coincidir con StartupWMClass
    app.setApplicationDisplayName("IdeaTracker v1.0")
    app.setDesktopFileName("ideaTracker")        # Wayland app_id
    app.setOrganizationName("IdeaTracker")
    app.setStyle("Fusion")

    # Default font
    font = QFont("Segoe UI", 11)
    app.setFont(font)

    # Global fix: text color is white on some Linux/Ubuntu themes
    app.setStyleSheet("""
        QWidget { color: #222222; }
        QLabel  { color: #222222; }
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
            color: #222222; background: #FFFFFF;
        }
        QComboBox {
            color: #222222; background: #FFFFFF;
        }
        QComboBox:!editable       { color: #222222; }
        QComboBox:!editable:on    { color: #222222; }
        QComboBox QAbstractItemView {
            color: #222222; background: #FFFFFF;
            selection-background-color: #E3F2FD;
            selection-color: #000000;
        }
        QComboBox QAbstractItemView::item          { color: #222222; }
        QComboBox QAbstractItemView::item:selected { color: #000000; }
        QTableWidget       { color: #222222; background: #FFFFFF; }
        QTableWidget::item { color: #222222; }
        QTableWidget::item:selected { color: #000000; background: #E3F2FD; }
        QHeaderView::section { color: #555555; background: #F8F9FA; }
        QListWidget       { color: #222222; background: #FFFFFF; }
        QListWidget::item { color: #222222; }
        QMessageBox       { background: #FFFFFF; color: #222222; }
        QMessageBox QLabel { color: #222222; background: transparent; }
        QMessageBox QPushButton {
            background: #FFFFFF; color: #222222;
            border: 1px solid #CCCCCC; border-radius: 5px;
            padding: 6px 18px; min-width: 70px;
        }
        QMessageBox QPushButton:hover  { background: #F0F0F0; }
        QMessageBox QPushButton:default {
            background: #2196F3; color: #FFFFFF;
            border: none;
        }
        QInputDialog       { background: #FFFFFF; color: #222222; }
        QInputDialog QLabel { color: #222222; background: transparent; }
        QInputDialog QLineEdit { color: #222222; background: #FFFFFF; }
        QDialog { background: #FFFFFF; }
    """)

    # App icon — title bar + taskbar
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "IdeaTracker.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
