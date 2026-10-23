from dataclasses import dataclass, replace
from typing import Generic, TypeVar, Union

from app.domain.models import EstadoTarea, Tarea


T = TypeVar("T")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T


@dataclass(frozen=True)
class Err:
    error: str


Result = Union[Ok[T], Err]


def validar_y_cambiar_estado(
    tarea: Tarea, nuevo_estado: EstadoTarea
) -> Result[Tarea]:
    match (tarea.estado, nuevo_estado):
        case (EstadoTarea.PENDIENTE, EstadoTarea.EN_PROGRESO):
            return Ok(replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_PROGRESO, EstadoTarea.EN_REVISION):
            return Ok(replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_REVISION, EstadoTarea.TERMINADA):
            return Ok(replace(tarea, estado=nuevo_estado))
        case (EstadoTarea.EN_REVISION, EstadoTarea.EN_PROGRESO):
            return Ok(replace(tarea, estado=nuevo_estado))
        case _:
            return Err(
                "Transición no permitida: "
                f"{tarea.estado.value} -> {nuevo_estado.value}"
            )
