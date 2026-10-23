from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class EstadoTarea(Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    EN_REVISION = "En revisión"
    TERMINADA = "Terminada"


class Prioridad(Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"


@dataclass(frozen=True)
class Integrante:
    id: int
    nombre: str
    email: str
    rol: str = ""


@dataclass(frozen=True)
class Proyecto:
    id: int
    nombre: str
    descripcion: str = ""
    integrante_ids: tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EntregableEDT:
    id: int
    proyecto_id: int
    nombre: str
    descripcion: str = ""
    padre_id: Optional[int] = None
    responsable_id: Optional[int] = None


@dataclass(frozen=True)
class Tarea:
    id: int
    entregable_id: int
    titulo: str
    descripcion: str = ""
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    prioridad: Prioridad = Prioridad.MEDIA
    responsable_id: Optional[int] = None
    orden: int = 0
