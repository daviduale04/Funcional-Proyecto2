from dataclasses import replace
from app.domain.models import EstadoTarea, Result, Ok, Err, Tarea

TRANSICIONES_PERMITIDAS: dict[EstadoTarea, set[EstadoTarea]] = {
    EstadoTarea.PENDIENTE: {EstadoTarea.EN_PROGRESO},
    EstadoTarea.EN_PROGRESO: {EstadoTarea.PENDIENTE, EstadoTarea.EN_REVISION},
    EstadoTarea.EN_REVISION: {EstadoTarea.EN_PROGRESO, EstadoTarea.TERMINADA},
    EstadoTarea.TERMINADA: {EstadoTarea.EN_REVISION},
}

def validar_y_cambiar_estado(tarea: Tarea, nuevo_estado: EstadoTarea) -> Result[Tarea]:
    """Valida la transición Kanban usando Pattern Matching estructural sin efectos colaterales."""
    match (tarea.estado, nuevo_estado):
        case (actual, destino) if actual == destino:
            return Err("La tarea ya se encuentra en ese estado.")
        case (actual, destino) if destino in TRANSICIONES_PERMITIDAS.get(actual, set()):
            # Inmutabilidad: replace() genera una nueva instancia
            return Ok(replace(tarea, estado=destino))
        case (actual, destino):
            return Err(f"Transición no permitida: no se puede pasar de '{actual.value}' a '{destino.value}'.")

def reasignar_responsable(tarea: Tarea, nuevo_responsable_id: int | None) -> Tarea:
    """Función pura para reasignar responsable inmutablemente."""
    return replace(tarea, responsable_id=nuevo_responsable_id)