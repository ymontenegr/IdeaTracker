from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Nota:
    fecha: str      # ISO format datetime string
    texto: str

    def to_dict(self) -> dict:
        return {"fecha": self.fecha, "texto": self.texto}

    @classmethod
    def from_dict(cls, data: dict) -> "Nota":
        return cls(fecha=data["fecha"], texto=data["texto"])

    def fecha_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.fecha)
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return self.fecha


@dataclass
class Idea:
    id: str
    nombre: str
    descripcion: str
    origen: str
    fecha_registro: str          # ISO datetime
    fecha_inicio_probable: str   # YYYY-MM-DD
    costo_aproximado: float
    beneficio_esperado: str
    categoria_id: str
    categoria_nombre: str
    prioridad: str               # Alta / Media / Baja
    estatus: str                 # Por iniciar / Iniciado / En proceso / Finalizado / Postergado / Cancelado
    notas: List[Nota] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "origen": self.origen,
            "fecha_registro": self.fecha_registro,
            "fecha_inicio_probable": self.fecha_inicio_probable,
            "costo_aproximado": self.costo_aproximado,
            "beneficio_esperado": self.beneficio_esperado,
            "categoria_id": self.categoria_id,
            "categoria_nombre": self.categoria_nombre,
            "prioridad": self.prioridad,
            "estatus": self.estatus,
            "notas": [n.to_dict() for n in self.notas],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Idea":
        notas = [Nota.from_dict(n) for n in data.get("notas", [])]
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            origen=data.get("origen", ""),
            fecha_registro=data["fecha_registro"],
            fecha_inicio_probable=data.get("fecha_inicio_probable", ""),
            costo_aproximado=float(data.get("costo_aproximado", 0)),
            beneficio_esperado=data.get("beneficio_esperado", ""),
            categoria_id=data.get("categoria_id", ""),
            categoria_nombre=data.get("categoria_nombre", ""),
            prioridad=data.get("prioridad", "Media"),
            estatus=data.get("estatus", "Por iniciar"),
            notas=notas,
        )

    def fecha_registro_display(self) -> str:
        try:
            dt = datetime.fromisoformat(self.fecha_registro)
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return self.fecha_registro

    def fecha_inicio_display(self) -> str:
        try:
            from datetime import date
            d = date.fromisoformat(self.fecha_inicio_probable)
            return d.strftime("%d/%m/%Y")
        except Exception:
            return self.fecha_inicio_probable

    def costo_display(self) -> str:
        try:
            return f"${self.costo_aproximado:,.2f}"
        except Exception:
            return str(self.costo_aproximado)

    def mes_registro(self) -> tuple:
        """Returns (year, month) tuple for filtering."""
        try:
            dt = datetime.fromisoformat(self.fecha_registro)
            return (dt.year, dt.month)
        except Exception:
            return (0, 0)


@dataclass
class Categoria:
    id: str
    nombre: str

    def to_dict(self) -> dict:
        return {"id": self.id, "nombre": self.nombre}

    @classmethod
    def from_dict(cls, data: dict) -> "Categoria":
        return cls(id=data["id"], nombre=data["nombre"])


@dataclass
class HistorialEstatus:
    estatus: str
    fecha: str   # ISO datetime

    def to_dict(self) -> dict:
        return {"estatus": self.estatus, "fecha": self.fecha}

    @classmethod
    def from_dict(cls, data: dict) -> "HistorialEstatus":
        return cls(estatus=data["estatus"], fecha=data["fecha"])

    def fecha_display(self) -> str:
        try:
            return datetime.fromisoformat(self.fecha).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return self.fecha


@dataclass
class Tarea:
    id: str
    nombre: str
    descripcion: str
    idea_id: str            # "default" si no pertenece a ninguna idea
    idea_nombre: str        # Nombre de la idea o "Sin proyecto"
    fecha_creacion: str     # ISO datetime (automático)
    estatus: str            # Por iniciar | Iniciada | Finalizada | Cerrada
    historial_estatus: List[HistorialEstatus] = field(default_factory=list)
    notas: List["Nota"] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "idea_id": self.idea_id,
            "idea_nombre": self.idea_nombre,
            "fecha_creacion": self.fecha_creacion,
            "estatus": self.estatus,
            "historial_estatus": [h.to_dict() for h in self.historial_estatus],
            "notas": [n.to_dict() for n in self.notas],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tarea":
        historial = [HistorialEstatus.from_dict(h)
                     for h in data.get("historial_estatus", [])]
        notas = [Nota.from_dict(n) for n in data.get("notas", [])]
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            idea_id=data.get("idea_id", "default"),
            idea_nombre=data.get("idea_nombre", "Sin proyecto"),
            fecha_creacion=data["fecha_creacion"],
            estatus=data.get("estatus", "Por iniciar"),
            historial_estatus=historial,
            notas=notas,
        )

    def fecha_creacion_display(self) -> str:
        try:
            return datetime.fromisoformat(self.fecha_creacion).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return self.fecha_creacion

    def fecha_ultimo_cambio_display(self) -> str:
        if self.historial_estatus:
            return self.historial_estatus[-1].fecha_display()
        return self.fecha_creacion_display()

    def es_independiente(self) -> bool:
        return self.idea_id == "default"
