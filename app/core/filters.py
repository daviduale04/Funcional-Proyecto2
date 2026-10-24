from typing import Callable, Iterable, Sequence
from app.domain.models import EstadoTarea, Prioridad, Tarea

def crear_filtro_responsable(responsable_id: int) -> Callable[[Tarea], bool]:
    """Closure que captura el responsable_id en su scope léxico."""
    return lambda tarea: tarea.responsable_id == responsable_id

def crear_filtro_estado(estado: EstadoTarea) -> Callable[[Tarea], bool]:
    """Closure que captura el estado objetivo."""
    return lambda tarea: tarea.estado == estado

def crear_filtro_prioridad(prioridad: Prioridad) -> Callable[[Tarea], bool]:
    """Closure que captura la prioridad."""
    return lambda tarea: tarea.prioridad == prioridad

def aplicar_filtros_combinados(
    tareas: Iterable[Tarea],
    *predicados: Callable[[Tarea], bool],
) -> list[Tarea]:
    """Función de Orden Superior (HOF) que aplica n predicados puros mediante filter()."""
    resultado = tareas
    for predicado in predicados:
        resultado = filter(predicado, resultado)
    return list(resultado)

def ordenar_tareas_por_prioridad(tareas: Sequence[Tarea]) -> list[Tarea]:
    """Uso de lambda pura para ordenar por peso de prioridad."""
    pesos = {Prioridad.ALTA: 1, Prioridad.MEDIA: 2, Prioridad.BAJA: 3}
    return sorted(tareas, key=lambda t: pesos.get(t.prioridad, 99))