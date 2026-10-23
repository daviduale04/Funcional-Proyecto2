from app.core.kanban import Err, Ok, validar_y_cambiar_estado
from app.domain.models import EstadoTarea, Tarea


def crear_tarea(estado: EstadoTarea = EstadoTarea.PENDIENTE) -> Tarea:
    return Tarea(id=1, entregable_id=1, titulo="Tarea de prueba", estado=estado)


def test_transicion_valida_pendiente_a_en_progreso():
    tarea = crear_tarea(EstadoTarea.PENDIENTE)

    resultado = validar_y_cambiar_estado(tarea, EstadoTarea.EN_PROGRESO)

    assert isinstance(resultado, Ok)
    assert resultado.value.estado is EstadoTarea.EN_PROGRESO
    assert tarea.estado is EstadoTarea.PENDIENTE


def test_transicion_invalida_pendiente_a_terminada():
    tarea = crear_tarea(EstadoTarea.PENDIENTE)

    resultado = validar_y_cambiar_estado(tarea, EstadoTarea.TERMINADA)

    assert isinstance(resultado, Err)
    assert "Pendiente" in resultado.error
    assert "Terminada" in resultado.error


def test_cambio_al_mismo_estado_retorna_err():
    tarea = crear_tarea(EstadoTarea.EN_PROGRESO)

    resultado = validar_y_cambiar_estado(tarea, EstadoTarea.EN_PROGRESO)

    assert isinstance(resultado, Err)
    assert "En progreso" in resultado.error
