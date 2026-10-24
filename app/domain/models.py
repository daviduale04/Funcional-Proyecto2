from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err:
    error: str

Result = Ok[T] | Err

class EstadoTarea(str, Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    EN_REVISION = "En revisión"
    TERMINADA = "Terminada"

class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"

@dataclass(frozen=True)
class Integrante:
    id: int
    nombre: str
    rol: str

@dataclass(frozen=True)
class Tarea:
    id: int
    id_entregable: int
    titulo: str
    descripcion: str
    responsable_id: Optional[int]
    prioridad: Prioridad
    estado: EstadoTarea

@dataclass(frozen=True)
class EntregableEDT:
    id: int
    id_proyecto: int
    nombre: str
    descripcion: str

@dataclass(frozen=True)
class Proyecto:
    id: int
    nombre: str
    descripcion: str