from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from .ideas_widget import IdeasWidget
from .tareas_widget import TareasWidget
from .reports_widget import ReportsWidget
from .config_widget import ConfigWidget


NAV_STYLE = """
QPushButton {
    background: transparent;
    color: #B0BEC5;
    border: none;
    border-radius: 8px;
    padding: 14px 20px;
    text-align: left;
    font-size: 14px;
}
QPushButton:hover {
    background: rgba(255,255,255,0.08);
    color: #FFFFFF;
}
QPushButton:checked {
    background: rgba(33, 150, 243, 0.25);
    color: #FFFFFF;
    border-left: 3px solid #2196F3;
}
"""

SIDEBAR_STYLE = """
QWidget#sidebar {
    background: #1A237E;
}
"""

MAIN_STYLE = """
QMainWindow {
    background: #F5F7FA;
}
QWidget#content {
    background: #F5F7FA;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IdeaTracker v1.1")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 780)
        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(central)

        # ── Sidebar ────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(4)

        logo_label = QLabel("IdeaTracker  v1.1")
        logo_label.setStyleSheet(
            "color: #FFFFFF; font-size: 20px; font-weight: bold; padding: 8px 8px 24px 8px;"
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        sidebar_layout.addWidget(logo_label)

        self.btn_ideas   = QPushButton("📝  Ideas")
        self.btn_tareas  = QPushButton("✅  Tareas")
        self.btn_reports = QPushButton("📊  Reportes")
        self.btn_config  = QPushButton("⚙️   Configuración")
        self.btn_exit    = QPushButton("🚪  Salir")

        for btn in (self.btn_ideas, self.btn_tareas, self.btn_reports, self.btn_config):
            btn.setCheckable(True)
            btn.setStyleSheet(NAV_STYLE)
            btn.setFont(QFont("Segoe UI", 13))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        self.btn_exit.setStyleSheet(NAV_STYLE + "QPushButton { color: #EF9A9A; }")
        self.btn_exit.setFont(QFont("Segoe UI", 13))
        sidebar_layout.addWidget(self.btn_exit)

        root_layout.addWidget(sidebar)

        # ── Content area ───────────────────────────────────
        content = QWidget()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.ideas_widget   = IdeasWidget()
        self.tareas_widget  = TareasWidget()
        self.reports_widget = ReportsWidget()
        self.config_widget  = ConfigWidget()

        self.stack.addWidget(self.ideas_widget)    # index 0
        self.stack.addWidget(self.tareas_widget)   # index 1
        self.stack.addWidget(self.reports_widget)  # index 2
        self.stack.addWidget(self.config_widget)   # index 3

        content_layout.addWidget(self.stack)
        root_layout.addWidget(content)

        # ── Signals ────────────────────────────────────────
        self.btn_ideas.clicked.connect(lambda:   self._navigate(0))
        self.btn_tareas.clicked.connect(lambda:  self._navigate(1))
        self.btn_reports.clicked.connect(lambda: self._navigate(2))
        self.btn_config.clicked.connect(lambda:  self._navigate(3))
        self.btn_exit.clicked.connect(self._exit_app)

        self.config_widget.categories_changed.connect(self.ideas_widget.refresh_categories)
        self.config_widget.categories_changed.connect(self.reports_widget.refresh)

        self._navigate(0)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        buttons = [self.btn_ideas, self.btn_tareas, self.btn_reports, self.btn_config]
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)

        if index == 0:
            self.ideas_widget.refresh()
        elif index == 1:
            self.tareas_widget.refresh()
        elif index == 2:
            self.reports_widget.refresh()

    def _exit_app(self):
        reply = QMessageBox.question(
            self, "Salir",
            "¿Estás seguro de que deseas cerrar IdeaTracker?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
