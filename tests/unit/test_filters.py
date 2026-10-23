from app.core.filters import (
    crear_filtro_estado,
    crear_filtro_responsable,
    filtrar_tareas,
)
from app.domain.models import EstadoTarea, Tarea


def crear_tarea(
    id: int,
    estado: EstadoTarea = EstadoTarea.PENDIENTE,
    responsable_id: int | None = None,
) -> Tarea:
    return Tarea(
        id=id,
        entregable_id=1,
        titulo=f"Tarea {id}",
        estado=estado,
        responsable_id=responsable_id,
    )


TAREAS = (
    crear_tarea(1, EstadoTarea.PENDIENTE, 10),
    crear_tarea(2, EstadoTarea.EN_PROGRESO, 10),
    crear_tarea(3, EstadoTarea.EN_PROGRESO, 20),
    crear_tarea(4, EstadoTarea.TERMINADA, None),
)


def test_filtro_por_responsable():
    predicado = crear_filtro_responsable(10)

    resultado = filtrar_tareas(TAREAS, predicado)

    assert [tarea.id for tarea in resultado] == [1, 2]


def test_filtro_por_estado():
    predicado = crear_filtro_estado(EstadoTarea.EN_PROGRESO)

    resultado = filtrar_tareas(TAREAS, predicado)

    assert [tarea.id for tarea in resultado] == [2, 3]


def test_filtro_responsable_ausente():
    predicado = crear_filtro_responsable(None)

    resultado = filtrar_tareas(TAREAS, predicado)

    assert [tarea.id for tarea in resultado] == [4]


def test_filtrar_combina_multiples_predicados():
    resultado = filtrar_tareas(
        TAREAS,
        crear_filtro_responsable(10),
        crear_filtro_estado(EstadoTarea.EN_PROGRESO),
    )

    assert [tarea.id for tarea in resultado] == [2]


def test_filtrar_sin_predicados_devuelve_todas():
    resultado = filtrar_tareas(TAREAS)

    assert resultado == list(TAREAS)
