import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import DATA_DIR, TAREAS_DIR, CONFIG_FILE, MAX_CATEGORIES, IDEA_DEFAULT_ID, IDEA_DEFAULT_NAME
from .models import Idea, Nota, Categoria, Tarea, HistorialEstatus


# ── Config / Categories ─────────────────────────────────────────────────────

def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_categories() -> List[Categoria]:
    config = load_config()
    return [Categoria.from_dict(c) for c in config.get("categorias", [])]


def save_categories(categories: List[Categoria]) -> None:
    config = load_config()
    config["categorias"] = [c.to_dict() for c in categories]
    save_config(config)


def add_category(nombre: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    cats = load_categories()
    if len(cats) >= MAX_CATEGORIES:
        return False, f"Has alcanzado el límite de {MAX_CATEGORIES} categorías. Elimina una para poder agregar otra."
    nombre_strip = nombre.strip()
    if not nombre_strip:
        return False, "El nombre de la categoría no puede estar vacío."
    for c in cats:
        if c.nombre.lower() == nombre_strip.lower():
            return False, f"Ya existe una categoría con el nombre '{nombre_strip}'."
    cats.append(Categoria(id=str(uuid.uuid4()), nombre=nombre_strip))
    save_categories(cats)
    return True, "Categoría creada exitosamente."


def edit_category(cat_id: str, nuevo_nombre: str) -> tuple[bool, str]:
    """Renames category and updates all ideas that reference it."""
    cats = load_categories()
    nuevo_nombre = nuevo_nombre.strip()
    if not nuevo_nombre:
        return False, "El nombre no puede estar vacío."
    for c in cats:
        if c.id != cat_id and c.nombre.lower() == nuevo_nombre.lower():
            return False, f"Ya existe una categoría con el nombre '{nuevo_nombre}'."

    old_nombre = None
    for c in cats:
        if c.id == cat_id:
            old_nombre = c.nombre
            c.nombre = nuevo_nombre
            break

    if old_nombre is None:
        return False, "Categoría no encontrada."

    save_categories(cats)

    # Update all ideas that reference this category
    ideas = load_all_ideas()
    for idea in ideas:
        if idea.categoria_id == cat_id:
            idea.categoria_nombre = nuevo_nombre
            save_idea(idea)

    return True, f"Categoría renombrada a '{nuevo_nombre}' y actualizada en todas las ideas."


def delete_category(cat_id: str) -> tuple[bool, str, int]:
    """Deletes category. Returns (success, message, affected_ideas_count)."""
    cats = load_categories()
    ideas = load_all_ideas()
    affected = sum(1 for i in ideas if i.categoria_id == cat_id)

    cats = [c for c in cats if c.id != cat_id]
    save_categories(cats)
    return True, "Categoría eliminada.", affected


def get_ideas_count_by_category(cat_id: str) -> int:
    return sum(1 for i in load_all_ideas() if i.categoria_id == cat_id)


# ── Ideas ────────────────────────────────────────────────────────────────────

def _idea_path(idea_id: str) -> Path:
    return DATA_DIR / f"{idea_id}.json"


def load_idea(idea_id: str) -> Optional[Idea]:
    path = _idea_path(idea_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return Idea.from_dict(json.load(f))


def save_idea(idea: Idea) -> None:
    path = _idea_path(idea.id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(idea.to_dict(), f, ensure_ascii=False, indent=2)


def delete_idea(idea_id: str) -> None:
    path = _idea_path(idea_id)
    if path.exists():
        path.unlink()


def load_all_ideas() -> List[Idea]:
    ideas = []
    for f in DATA_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                ideas.append(Idea.from_dict(json.load(fp)))
        except Exception:
            pass
    return ideas


def create_idea(
    nombre: str,
    descripcion: str,
    origen: str,
    fecha_inicio_probable: str,
    costo_aproximado: float,
    beneficio_esperado: str,
    categoria_id: str,
    categoria_nombre: str,
    prioridad: str,
) -> Idea:
    idea = Idea(
        id=str(uuid.uuid4()),
        nombre=nombre,
        descripcion=descripcion,
        origen=origen,
        fecha_registro=datetime.now().isoformat(timespec="seconds"),
        fecha_inicio_probable=fecha_inicio_probable,
        costo_aproximado=costo_aproximado,
        beneficio_esperado=beneficio_esperado,
        categoria_id=categoria_id,
        categoria_nombre=categoria_nombre,
        prioridad=prioridad,
        estatus="Por iniciar",
        notas=[],
    )
    save_idea(idea)
    return idea


def add_nota(idea_id: str, texto: str) -> Optional[Idea]:
    idea = load_idea(idea_id)
    if idea is None:
        return None
    nota = Nota(
        fecha=datetime.now().isoformat(timespec="seconds"),
        texto=texto.strip(),
    )
    idea.notas.append(nota)
    save_idea(idea)
    return idea


# ── Tareas ───────────────────────────────────────────────────────────────────

def _tarea_path(tarea_id: str) -> Path:
    return TAREAS_DIR / f"{tarea_id}.json"


def load_tarea(tarea_id: str) -> Optional[Tarea]:
    path = _tarea_path(tarea_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return Tarea.from_dict(json.load(f))


def save_tarea(tarea: Tarea) -> None:
    with open(_tarea_path(tarea.id), "w", encoding="utf-8") as f:
        json.dump(tarea.to_dict(), f, ensure_ascii=False, indent=2)


def delete_tarea(tarea_id: str) -> None:
    path = _tarea_path(tarea_id)
    if path.exists():
        path.unlink()


def load_all_tareas() -> List[Tarea]:
    tareas = []
    for f in TAREAS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                tareas.append(Tarea.from_dict(json.load(fp)))
        except Exception:
            pass
    return tareas


def load_tareas_by_idea(idea_id: str) -> List[Tarea]:
    return [t for t in load_all_tareas() if t.idea_id == idea_id]


def create_tarea(
    nombre: str,
    descripcion: str,
    idea_id: str = IDEA_DEFAULT_ID,
    idea_nombre: str = IDEA_DEFAULT_NAME,
) -> Tarea:
    now = datetime.now().isoformat(timespec="seconds")
    tarea = Tarea(
        id=str(uuid.uuid4()),
        nombre=nombre,
        descripcion=descripcion,
        idea_id=idea_id,
        idea_nombre=idea_nombre,
        fecha_creacion=now,
        estatus="Por iniciar",
        historial_estatus=[HistorialEstatus(estatus="Por iniciar", fecha=now)],
    )
    save_tarea(tarea)
    return tarea


def cambiar_estatus_tarea(tarea_id: str, nuevo_estatus: str) -> Optional[Tarea]:
    tarea = load_tarea(tarea_id)
    if tarea is None:
        return None
    tarea.estatus = nuevo_estatus
    tarea.historial_estatus.append(
        HistorialEstatus(
            estatus=nuevo_estatus,
            fecha=datetime.now().isoformat(timespec="seconds"),
        )
    )
    save_tarea(tarea)
    return tarea
