import sqlite3
from typing import Optional
from app.domain.models import EstadoTarea, Integrante, Prioridad, Proyecto, Tarea, EntregableEDT

# Ruta predeterminada de la base de datos local SQLite
DB_PATH = "gestor_proyectos.db"

def init_db(db_path: str = DB_PATH) -> None:
    """Crea las tablas iniciales en SQLite y precarga datos completos de prueba."""
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
                           ("Gestor de Proyectos", "Sistema de Planificación EDT y Kanban"))
            
            # Integrantes
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (1, 'Marta Ruiz', 'Desarrolladora')")
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (2, 'Luis Gómez', 'Analista')")
            cursor.execute("INSERT INTO integrantes (id, nombre, rol) VALUES (3, 'Ana Torres', 'Arquitecta')")

            # Entregables EDT
            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (1, 1, 'Entregable #1', 'Definición y requisitos')")
            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (2, 1, 'Entregable #2', 'Diseño e implementación')")
            cursor.execute("INSERT INTO entregables (id, id_proyecto, nombre, descripcion) VALUES (3, 1, 'Entregable #3', 'Pruebas y documentación')")

            # Tareas precargadas
            cursor.execute("""
                INSERT INTO tareas (id_entregable, titulo, descripcion, responsable_id, prioridad, estado) VALUES
                (1, 'Definir alcance del proyecto', 'Reunión de kickoff y alcance', 3, 'Alta', 'Terminada'),
                (1, 'Levantar requisitos funcionales', 'Casos de uso y reglas de negocio', 3, 'Media', 'En revisión'),
                (2, 'Diseñar modelo de datos', 'Esquema relacional e inmutabilidad', 2, 'Alta', 'En progreso'),
                (2, 'Implementar tablero Kanban', 'Componentes visuales y eventos', 2, 'Alta', 'En progreso'),
                (3, 'Crear pruebas de transición', 'Verificar reglas del Functional Core', 1, 'Media', 'Pendiente'),
                (3, 'Documentar funcionamiento', 'Redactar informe y evidencias', 3, 'Baja', 'Pendiente')
            """)
        conn.commit()

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

def insertar_tarea(tarea: Tarea, db_path: str = DB_PATH) -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tareas (id_entregable, titulo, descripcion, responsable_id, prioridad, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tarea.id_entregable, tarea.titulo, tarea.descripcion, tarea.responsable_id, tarea.prioridad.value, tarea.estado.value))
        conn.commit()
        return cursor.lastrowid

def actualizar_estado_tarea_db(id_tarea: int, nuevo_estado: EstadoTarea, db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tareas SET estado = ? WHERE id = ?", (nuevo_estado.value, id_tarea))
        conn.commit()