import os
import json
import uuid
from pathlib import Path

APP_DIR = Path.home() / "IdeaTracker"
DATA_DIR = APP_DIR / "data"
TAREAS_DIR = APP_DIR / "tareas"
EXPORTS_DIR = APP_DIR / "exports"
CONFIG_FILE = APP_DIR / "config.json"

TAREA_STATUS_LIST = [
    "Por iniciar",
    "Iniciada",
    "Finalizada",
    "Cerrada",
]

TAREA_STATUS_COLORS = {
    "Por iniciar": "#2196F3",   # Blue
    "Iniciada":    "#FFC107",   # Yellow
    "Finalizada":  "#4CAF50",   # Green
    "Cerrada":     "#9E9E9E",   # Grey
}

IDEA_DEFAULT_ID   = "default"
IDEA_DEFAULT_NAME = "Sin proyecto"

MAX_CATEGORIES = 10

STATUS_LIST = [
    "Por iniciar",
    "Iniciado",
    "En proceso",
    "Finalizado",
    "Postergado",
    "Cancelado",
]

STATUS_COLORS = {
    "Por iniciar": "#2196F3",   # Blue
    "Iniciado":    "#FFC107",   # Yellow
    "En proceso":  "#FF9800",   # Orange
    "Finalizado":  "#4CAF50",   # Green
    "Postergado":  "#9E9E9E",   # Grey
    "Cancelado":   "#F44336",   # Red
}

STATUS_ICONS = {
    "Por iniciar": "🔵",
    "Iniciado":    "🟡",
    "En proceso":  "🟠",
    "Finalizado":  "🟢",
    "Postergado":  "⚫",
    "Cancelado":   "🔴",
}

PRIORIDADES = ["Alta", "Media", "Baja"]

PRIORIDAD_COLORS = {
    "Alta":  "#F44336",
    "Media": "#FF9800",
    "Baja":  "#4CAF50",
}

ORIGENES_DEFAULT = [
    "Reunión",
    "Lectura",
    "Conversación",
    "Análisis propio",
    "Investigación",
    "Evento",
    "Otro",
]

DEFAULT_CATEGORIES = [
    {"id": str(uuid.uuid4()), "nombre": "Planes de Negocio"},
    {"id": str(uuid.uuid4()), "nombre": "Compras"},
    {"id": str(uuid.uuid4()), "nombre": "Finanzas"},
    {"id": str(uuid.uuid4()), "nombre": "Viajes"},
    {"id": str(uuid.uuid4()), "nombre": "Tecnología"},
    {"id": str(uuid.uuid4()), "nombre": "Personal"},
    {"id": str(uuid.uuid4()), "nombre": "Operaciones"},
    {"id": str(uuid.uuid4()), "nombre": "Comercial"},
    {"id": str(uuid.uuid4()), "nombre": "Educación"},
    {"id": str(uuid.uuid4()), "nombre": "Otros"},
]


def setup_directories():
    """Create app directories and config.json if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TAREAS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        config = {"categorias": DEFAULT_CATEGORIES}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
