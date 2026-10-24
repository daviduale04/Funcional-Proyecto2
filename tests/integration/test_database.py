import os
import pytest
from app.adapters import database
from app.domain.models import EstadoTarea, Prioridad

@pytest.fixture
def db_test(tmp_path):
    """Crea un archivo temporal de base de datos SQLite para cada prueba."""
    db_file = str(tmp_path / "test_gestor.db")
    database.init_db(db_file)
    yield db_file
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except OSError:
            pass

def test_listar_y_actualizar_tarea_sqlite(db_test):
    tareas = database.listar_tareas(db_test)
    assert len(tareas) > 0

    tarea_inicial = tareas[0]
    database.actualizar_estado_tarea_db(tarea_inicial.id, EstadoTarea.EN_PROGRESO, db_test)

    actualizadas = database.listar_tareas(db_test)
    modificada = [t for t in actualizadas if t.id == tarea_inicial.id][0]
    assert modificada.estado == EstadoTarea.EN_PROGRESO

def test_insertar_y_eliminar_tarea_sqlite(db_test):
    id_creado = database.insertar_tarea_db(
        id_entregable=1,
        titulo="Tarea Temporal",
        descripcion="Prueba I/O",
        responsable_id=1,
        prioridad=Prioridad.ALTA,
        db_path=db_test,
    )
    assert id_creado > 0

    database.eliminar_tarea_db(id_creado, db_test)
    tareas = database.listar_tareas(db_test)
    ids = [t.id for t in tareas]
    assert id_creado not in ids