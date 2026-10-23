from dataclasses import dataclass
from typing import Generic, TypeVar
from app.domain.models import Tarea, EstadoTarea

T = TypeVar("T")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err:
    error: str

Result = Ok[T] | Err

def validar_y_cambiar_estado(tarea: Tarea, nuevo_estado: EstadoTarea) -> Result[Tarea]:
    """Transición pura de estados en Kanban usando pattern matching."""
    match (tarea.estado, nuevo_estado):
        # Transiciones permitidas
        case (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO):
            return Ok(dataclass_replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_PROGRESO, EstadoTarea.EN_REVISION):
            return Ok(dataclass_replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_REVISION, EstadoTarea.TERMINADA):
            return Ok(dataclass_replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_REVISION, EstadoTarea.EN_PROGRESO): # Regreso por correcciones
            return Ok(dataclass_replace(tarea, estado=nuevo_estado))
        
        # Mismo estado (sin cambio)
        case (estado_actual, estado_destino) if estado_actual == estado_destino:
            return Err("La tarea ya se encuentra en ese estado.")
        
        # Cualquier otra transición no permitida
        case (origen, destino):
            return Err(f"Transición no permitida: no se puede pasar de '{origen.value}' a '{destino.value}'.")

def dataclass_replace(tarea: Tarea, **kwargs) -> Tarea:
    """Helper para crear una copia inmutable con valores actualizados."""
    data = {field: getattr(tarea, field) for field in tarea.__annotations__}
    data.update(kwargs)
    return Tarea(**data)