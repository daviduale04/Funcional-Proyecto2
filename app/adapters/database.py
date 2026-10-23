import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.domain.models import EstadoTarea, Prioridad, Tarea


RutaBD = str | Path


_ESQUEMA = """
CREATE TABLE IF NOT EXISTS proyectos (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS integrantes (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY,
    entregable_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    estado TEXT NOT NULL,
    prioridad TEXT NOT NULL,
    responsable_id INTEGER,
    orden INTEGER NOT NULL DEFAULT 0
);
"""


@contextmanager
def _conexion(db_path: RutaBD) -> Iterator[sqlite3.Connection]:
    conexion = sqlite3.connect(db_path)
    try:
        yield conexion
        conexion.commit()
    finally:
        conexion.close()


def _enum_desde_texto(enum_clase, valor: str):
    for miembro in enum_clase:
        if valor in (miembro.value, miembro.name):
            return miembro
    opciones = ", ".join(miembro.value for miembro in enum_clase)
    raise ValueError(
        f"Valor '{valor}' no válido para {enum_clase.__name__}. "
        f"Opciones: {opciones}"
    )


def init_db(db_path: RutaBD) -> None:
    with _conexion(db_path) as conexion:
        conexion.executescript(_ESQUEMA)


def insertar_tarea(tarea: Tarea, db_path: RutaBD) -> None:
    with _conexion(db_path) as conexion:
        conexion.execute(
            """
            INSERT INTO tareas (
                id, entregable_id, titulo, descripcion,
                estado, prioridad, responsable_id, orden
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tarea.id,
                tarea.entregable_id,
                tarea.titulo,
                tarea.descripcion,
                tarea.estado.value,
                tarea.prioridad.value,
                tarea.responsable_id,
                tarea.orden,
            ),
        )


def obtener_todas_las_tareas(db_path: RutaBD) -> list[Tarea]:
    with _conexion(db_path) as conexion:
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(
            """
            SELECT id, entregable_id, titulo, descripcion,
                   estado, prioridad, responsable_id, orden
            FROM tareas
            ORDER BY orden, id
            """
        ).fetchall()

    return [
        Tarea(
            id=fila["id"],
            entregable_id=fila["entregable_id"],
            titulo=fila["titulo"],
            descripcion=fila["descripcion"],
            estado=_enum_desde_texto(EstadoTarea, fila["estado"]),
            prioridad=_enum_desde_texto(Prioridad, fila["prioridad"]),
            responsable_id=fila["responsable_id"],
            orden=fila["orden"],
        )
        for fila in filas
    ]


def actualizar_estado_tarea(
    id_tarea: int, nuevo_estado: str, db_path: RutaBD
) -> None:
    estado = _enum_desde_texto(EstadoTarea, nuevo_estado)
    with _conexion(db_path) as conexion:
        conexion.execute(
            "UPDATE tareas SET estado = ? WHERE id = ?",
            (estado.value, id_tarea),
        )
