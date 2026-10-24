import sqlite3
from typing import Optional
from app.adapters.decorators import medir_tiempo_db
from app.domain.models import EstadoTarea, Integrante, Prioridad, Proyecto, Tarea, EntregableEDT

DB_PATH = "gestor_proyectos.db"

def init_db(db_path: str = DB_PATH) -> None:
    """Crea las tablas iniciales en SQLite y precarga datos iniciales si está vacía."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS integrantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entregables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_proyecto INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_entregable INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                responsable_id INTEGER,
                prioridad TEXT NOT NULL,
                estado TEXT NOT NULL
            );
        """)

        cursor.execute("SELECT COUNT(*) FROM tareas")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO proyectos (nombre, descripcion) VALUES (?, ?)", 
                           ("Gestor Funcional", "Sistema de Planificación EDT y Kanban"))
            
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (1, 'David Guale', 'Desarrollador Core')")
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (2, 'Marta Ruiz', 'Analista de Negocio')")
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (3, 'Ana Torres', 'Arquitecta de Software')")

            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (1, 1, '1.0 Alcance y Arquitectura', 'Definición de modelos inmutables')")
            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (2, 1, '2.0 Núcleo Funcional', 'Reglas puras, closures y transiciones')")
            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (3, 1, '3.0 Shell e Interfaz', 'Persistencia SQLite y componentes ReactPy')")

            cursor.execute("""
                INSERT INTO tareas (id_entregable, titulo, descripcion, responsable_id, prioridad, estado) VALUES
                (1, 'Definir alcance del proyecto', 'Kickoff y especificación de requisitos', 3, 'Alta', 'Terminada'),
                (1, 'Modelar entidades inmutables', 'Creación de dataclasses frozen en domain', 1, 'Alta', 'En revisión'),
                (2, 'Implementar motor de transiciones', 'Pattern matching para control Kanban', 1, 'Alta', 'En progreso'),
                (2, 'Diseñar closures de filtrado', 'Filtros combinables por responsable y estado', 2, 'Media', 'En progreso'),
                (3, 'Crear vistas ReactPy', 'Tablero dinámico y vista EDT jerárquica', 1, 'Media', 'Pendiente'),
                (3, 'Elaborar suite de pruebas', 'Tests unitarios con pytest', 2, 'Baja', 'Pendiente')
            """)
        conn.commit()

@medir_tiempo_db
def listar_tareas(db_path: str = DB_PATH) -> list[Tarea]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_entregable, titulo, descripcion, responsable_id, prioridad, estado FROM tareas")
        return [
            Tarea(
                id=r[0],
                id_entregable=r[1],
                titulo=r[2],
                descripcion=r[3],
                responsable_id=r[4],
                prioridad=Prioridad(r[5]),
                estado=EstadoTarea(r[6]),
            )
            for r in cursor.fetchall()
        ]

def listar_entregables(db_path: str = DB_PATH) -> list[EntregableEDT]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_proyecto, nombre, descripcion FROM entregables")
        return [EntregableEDT(id=r[0], id_proyecto=r[1], nombre=r[2], descripcion=r[3]) for r in cursor.fetchall()]

def listar_integrantes(db_path: str = DB_PATH) -> list[Integrante]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, rol FROM integrantes")
        return [Integrante(id=r[0], nombre=r[1], rol=r[2]) for r in cursor.fetchall()]

@medir_tiempo_db
def insertar_tarea_db(id_entregable: int, titulo: str, descripcion: str, responsable_id: Optional[int], prioridad: Prioridad, db_path: str = DB_PATH) -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tareas (id_entregable, titulo, descripcion, responsable_id, prioridad, estado)
            VALUES (?, ?, ?, ?, ?, 'Pendiente')
        """, (id_entregable, titulo, descripcion, responsable_id, prioridad.value))
        conn.commit()
        return cursor.lastrowid or 0

@medir_tiempo_db
def actualizar_estado_tarea_db(id_tarea: int, nuevo_estado: EstadoTarea, db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tareas SET estado = ? WHERE id = ?", (nuevo_estado.value, id_tarea))
        conn.commit()

@medir_tiempo_db
def eliminar_tarea_db(id_tarea: int, db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tareas WHERE id = ?", (id_tarea,))
        conn.commit()