from typing import Callable, Iterable, Sequence
from app.domain.models import EstadoTarea, Prioridad, Tarea

# Closures configurables
def crear_filtro_responsable(responsable_id: int) -> Callable[[Tarea], bool]:
    """Retorna una función que filtra por responsable capturando su ID."""
    return lambda tarea: tarea.responsable_id == responsable_id

def crear_filtro_estado(estado: EstadoTarea) -> Callable[[Tarea], bool]:
    """Retorna una función que filtra por estado."""
    return lambda tarea: tarea.estado == estado

def crear_filtro_prioridad(prioridad: Prioridad) -> Callable[[Tarea], bool]:
    """Retorna una función que filtra por prioridad."""
    return lambda tarea: tarea.prioridad == prioridad

# Función de Orden Superior (HOF) requerida por el test
def aplicar_filtros_combinados(
    tareas: Iterable[Tarea],
    *predicados: Callable[[Tarea], bool],
) -> list[Tarea]:
    """HOF que reduce una secuencia de tareas aplicando múltiples predicados puros."""
    resultado = tareas
    for predicado in predicados:
        resultado = filter(predicado, resultado)
    return list(resultado)

def ordenar_tareas_por_prioridad(tareas: Sequence[Tarea]) -> list[Tarea]:
    """Uso de lambda como clave pequeña de ordenamiento."""
    peso_prioridad = {Prioridad.ALTA: 1, Prioridad.MEDIA: 2, Prioridad.BAJA: 3}
    return sorted(tareas, key=lambda t: peso_prioridad.get(t.prioridad, 99))