# Gestor de Proyectos: EDT & Kanban (Programación Funcional)

Aplicación web local desarrollada en Python para la planificación, descomposición jerárquica de trabajo mediante **Estructura de Desglose del Trabajo (EDT/WBS)** y seguimiento de flujo en un tablero **Kanban**. 

El sistema implementa estrictamente el patrón arquitectónico **Functional Core / Imperative Shell**, separando todas las reglas del negocio y transformaciones puras de los efectos colaterales (I/O, base de datos SQLite y renderizado web).

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.10+
- **Frontend Reactivo:** ReactPy
- **Servidor Web:** FastAPI + Uvicorn
- **Persistencia Local:** SQLite3
- **Testing:** Pytest

---

## 🏗️ Arquitectura del Sistema

```text
app/
  domain/       # Modelos inmutables, enums y tipos Result (Ok | Err)
  core/         # Functional Core: reglas puras, transiciones, filtros y EDT
  adapters/     # Imperative Shell: persistencia SQLite y decoradores
  ui/           # Imperative Shell: componentes reactivos ReactPy
  main.py       # Ensamblador de FastAPI y ReactPy
tests/
  unit/         # Pruebas unitarias puras del Core
  integration/  # Pruebas de integración del adaptador SQLite