import time
from functools import wraps
from typing import Callable, Any

def medir_tiempo_db(funcion: Callable[..., Any]) -> Callable[..., Any]:
    """Decorador transversal para medir duración de operaciones I/O en SQLite."""
    @wraps(funcion)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        fin = time.perf_counter()
        duracion_ms = (fin - inicio) * 1000
        print(f"[SHELL I/O] '{funcion.__name__}' completada en {duracion_ms:.2f} ms")
        return resultado
    return wrapper