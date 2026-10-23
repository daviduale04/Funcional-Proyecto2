from fastapi import FastAPI
from reactpy.backend.fastapi import configure
from app.adapters.database import init_db
from app.ui.components import TableroKanban

# Inicializar esquema SQLite
init_db()

app = FastAPI(title="Gestor de Proyectos Funcional")

# Compatibilidad: mapea el método que ReactPy espera hacia el método de FastAPI
if not hasattr(app, "add_websocket_route"):
    app.add_websocket_route = app.add_api_websocket_route

# Configurar el componente de ReactPy
configure(app, TableroKanban)