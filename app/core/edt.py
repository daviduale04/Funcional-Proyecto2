from typing import Sequence
from app.domain.models import EntregableEDT, Tarea, Result, Ok, Err, Prioridad, EstadoTarea

def validar_creacion_tarea(
    id_tarea: int,
    id_entregable: int,
    titulo: str,
    descripcion: str,
    prioridad: Prioridad,
    responsable_id: int | None = None,
) -> Result[Tarea]:
    """Función pura que valida datos requeridos antes de instanciar una Tarea."""
    if not titulo.strip():
        return Err("El título de la tarea no puede estar vacío.")
    if id_entregable <= 0:
        return Err("La tarea debe estar asociada a un entregable válido.")

    nueva_tarea = Tarea(
        id=id_tarea,
        id_entregable=id_entregable,
        titulo=titulo.strip(),
        descripcion=descripcion.strip(),
        responsable_id=responsable_id,
        prioridad=prioridad,
        estado=EstadoTarea.PENDIENTE,
    )
    return Ok(nueva_tarea)

def agrupar_tareas_por_entregable(
    entregables: Sequence[EntregableEDT],
    tareas: Sequence[Tarea],
) -> dict[int, list[Tarea]]:
    """Función pura que agrupa tareas bajo la clave de su entregable correspondiente."""
    return {
        entregable.id: [t for t in tareas if t.id_entregable == entregable.id]
        for entregable in entregables
    }