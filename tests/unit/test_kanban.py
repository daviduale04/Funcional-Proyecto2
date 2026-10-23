import pytest
from app.domain.models import Tarea, EstadoTarea, Prioridad, Ok, Err
from app.core.kanban import validar_y_cambiar_estado
from app.core.filters import crear_filtro_estado, crear_filtro_responsable, aplicar_filtros_combinados

@pytest.fixture
def tarea_ejemplo():
    return Tarea(
        id=1,
        id_entregable=10,
        titulo="Prueba Unitaria",
        descripcion="Verificar transiciones de estado",
        responsable_id=2,
        prioridad=Prioridad.ALTA,
        estado=EstadoTarea.PENDIENTE,
    )

def test_transicion_valida_pendiente_a_en_progreso(tarea_ejemplo):
    resultado = validar_y_cambiar_estado(tarea_ejemplo, EstadoTarea.EN_PROGRESO)
    assert type(resultado).__name__ == "Ok"
    assert resultado.value.estado == EstadoTarea.EN_PROGRESO

def test_transicion_invalida_salto_prohibido(tarea_ejemplo):
    resultado = validar_y_cambiar_estado(tarea_ejemplo, EstadoTarea.TERMINADA)
    assert type(resultado).__name__ == "Err"
    assert "Transición no permitida" in resultado.error

def test_transicion_mismo_estado_rechazada(tarea_ejemplo):
    resultado = validar_y_cambiar_estado(tarea_ejemplo, EstadoTarea.PENDIENTE)
    assert type(resultado).__name__ == "Err"
    assert "ya se encuentra en ese estado" in resultado.error

def test_closures_de_filtrado(tarea_ejemplo):
    filtro_resp = crear_filtro_responsable(2)
    filtro_estado = crear_filtro_estado(EstadoTarea.PENDIENTE)
    
    lista = [tarea_ejemplo]
    resultado = aplicar_filtros_combinados(lista, filtro_resp, filtro_estado)
    assert len(resultado) == 1
    
    filtro_otro_resp = crear_filtro_responsable(99)
    resultado_vacio = aplicar_filtros_combinados(lista, filtro_otro_resp)
    assert len(resultado_vacio) == 0