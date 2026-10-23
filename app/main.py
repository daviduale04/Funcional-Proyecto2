import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from reactpy import component, html
from reactpy.backend.fastapi import configure

from app.adapters.database import (
    init_db,
    insertar_tarea,
    obtener_todas_las_tareas,
)
from app.domain.models import EstadoTarea, Integrante, Prioridad, Tarea
from app.ui.components import tablero_kanban


DB_PATH = Path(
    os.environ.get(
        "GESTOR_DB_PATH",
        Path(__file__).resolve().parent.parent / "gestor_proyectos.db",
    )
)

INTEGRANTES = (
    Integrante(
        id=1,
        nombre="Ana Torres",
        email="ana.torres@example.com",
        rol="Líder de proyecto",
    ),
    Integrante(
        id=2,
        nombre="Luis Gómez",
        email="luis.gomez@example.com",
        rol="Desarrollador",
    ),
    Integrante(
        id=3,
        nombre="Marta Ruiz",
        email="marta.ruiz@example.com",
        rol="QA",
    ),
)

TAREAS_INICIALES = (
    Tarea(
        id=1,
        entregable_id=1,
        titulo="Definir alcance del proyecto",
        descripcion="Documentar objetivos y límites del proyecto.",
        estado=EstadoTarea.TERMINADA,
        prioridad=Prioridad.ALTA,
        responsable_id=1,
        orden=1,
    ),
    Tarea(
        id=2,
        entregable_id=1,
        titulo="Levantar requisitos funcionales",
        descripcion="Recopilar necesidades de los usuarios.",
        estado=EstadoTarea.EN_REVISION,
        prioridad=Prioridad.MEDIA,
        responsable_id=1,
        orden=2,
    ),
    Tarea(
        id=3,
        entregable_id=2,
        titulo="Diseñar modelo de datos",
        descripcion="Modelar entidades inmutables del dominio.",
        estado=EstadoTarea.EN_PROGRESO,
        prioridad=Prioridad.ALTA,
        responsable_id=2,
        orden=1,
    ),
    Tarea(
        id=4,
        entregable_id=2,
        titulo="Implementar tablero Kanban",
        descripcion="Construir columnas y tarjetas del tablero.",
        estado=EstadoTarea.EN_PROGRESO,
        prioridad=Prioridad.ALTA,
        responsable_id=2,
        orden=2,
    ),
    Tarea(
        id=5,
        entregable_id=3,
        titulo="Crear pruebas de transición",
        descripcion="Validar cambios de estado permitidos.",
        estado=EstadoTarea.PENDIENTE,
        prioridad=Prioridad.MEDIA,
        responsable_id=3,
        orden=1,
    ),
    Tarea(
        id=6,
        entregable_id=3,
        titulo="Documentar funcionamiento",
        descripcion="Preparar guía de uso del gestor.",
        estado=EstadoTarea.PENDIENTE,
        prioridad=Prioridad.BAJA,
        responsable_id=1,
        orden=2,
    ),
)


def _sembrar_datos_si_vacio() -> None:
    if obtener_todas_las_tareas(DB_PATH):
        return
    for tarea in TAREAS_INICIALES:
        insertar_tarea(tarea, DB_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DB_PATH)
    _sembrar_datos_si_vacio()
    yield


app = FastAPI(title="Gestor de Proyectos", lifespan=lifespan)


@component
def vista_principal():
    tareas = obtener_todas_las_tareas(DB_PATH)
    return html.div(
        html.h1(
            {"style": {"margin": "0 0 1rem 0"}},
            "Gestor de Proyectos",
        ),
        tablero_kanban(
            tareas_iniciales=tareas,
            db_path=DB_PATH,
            integrantes=INTEGRANTES,
        ),
    )


configure(app.router, vista_principal)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
