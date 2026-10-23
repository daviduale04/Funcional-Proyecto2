from typing import Callable, Iterable, Optional

from app.domain.models import EstadoTarea, Tarea


PredicadoTarea = Callable[[Tarea], bool]


def crear_filtro_responsable(responsable_id: Optional[int]) -> PredicadoTarea:
    return lambda tarea: tarea.responsable_id == responsable_id


def crear_filtro_estado(estado: EstadoTarea) -> PredicadoTarea:
    return lambda tarea: tarea.estado is estado


def filtrar_tareas(
    tareas: Iterable[Tarea], *predicados: PredicadoTarea
) -> list[Tarea]:
    return [
        tarea
        for tarea in tareas
        if all(predicado(tarea) for predicado in predicados)
    ]
