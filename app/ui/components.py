from collections import defaultdict
from pathlib import Path
from typing import Iterable

from reactpy import component, hooks, html

from app.adapters.database import actualizar_estado_tarea
from app.core.kanban import Err, Ok, validar_y_cambiar_estado
from app.domain.models import EstadoTarea, Integrante, Prioridad, Tarea


COLUMNAS = (
    EstadoTarea.PENDIENTE,
    EstadoTarea.EN_PROGRESO,
    EstadoTarea.EN_REVISION,
    EstadoTarea.TERMINADA,
)

COLOR_PRIORIDAD = {
    Prioridad.BAJA: "#2f855a",
    Prioridad.MEDIA: "#b7791f",
    Prioridad.ALTA: "#c53030",
}

ESTILO_TABLERO = {
    "display": "flex",
    "gap": "1rem",
    "alignItems": "flex-start",
    "overflowX": "auto",
    "padding": "0.5rem 0",
}

ESTILO_COLUMNA = {
    "flex": "1 1 0",
    "minWidth": "220px",
    "backgroundColor": "#f4f5f7",
    "borderRadius": "10px",
    "padding": "0.75rem",
    "boxSizing": "border-box",
}

ESTILO_TARJETA = {
    "backgroundColor": "#ffffff",
    "borderRadius": "8px",
    "padding": "0.75rem",
    "marginBottom": "0.75rem",
    "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.15)",
}

ESTILO_BOTON = {
    "fontSize": "0.75rem",
    "padding": "0.25rem 0.5rem",
    "margin": "0.15rem",
    "border": "1px solid #cbd5e0",
    "borderRadius": "6px",
    "backgroundColor": "#ffffff",
    "cursor": "pointer",
}

ESTILO_PANEL = {
    "backgroundColor": "#edf2f7",
    "borderRadius": "10px",
    "padding": "0.75rem 1rem",
    "marginBottom": "1rem",
}


def _mapa_integrantes(integrantes: Iterable[Integrante]) -> dict[int, str]:
    return {integrante.id: integrante.nombre for integrante in integrantes}


def _nombre_responsable(
    responsable_id: int | None, integrantes: dict[int, str]
) -> str:
    if responsable_id is None:
        return "Sin asignar"
    return integrantes.get(responsable_id, f"Integrante {responsable_id}")


def _agrupar_por_entregable(tareas: Iterable[Tarea]) -> dict[int, list[Tarea]]:
    grupos: dict[int, list[Tarea]] = defaultdict(list)
    for tarea in tareas:
        grupos[tarea.entregable_id].append(tarea)
    return dict(sorted(grupos.items()))


@component
def tarjeta_tarea(
    tarea: Tarea,
    integrantes: dict[int, str],
    al_transicionar,
):
    def manejar_clic(evento, nuevo_estado: EstadoTarea):
        al_transicionar(tarea, nuevo_estado)

    return html.div(
        {"style": ESTILO_TARJETA},
        html.div(
            {"style": {"fontWeight": "600", "marginBottom": "0.4rem"}},
            tarea.titulo,
        ),
        html.div(
            {"style": {"fontSize": "0.8rem", "color": "#4a5568"}},
            f"Responsable: {_nombre_responsable(tarea.responsable_id, integrantes)}",
        ),
        html.div(
            {
                "style": {
                    "display": "inline-block",
                    "fontSize": "0.75rem",
                    "fontWeight": "600",
                    "color": "#ffffff",
                    "backgroundColor": COLOR_PRIORIDAD[tarea.prioridad],
                    "borderRadius": "999px",
                    "padding": "0.1rem 0.5rem",
                    "marginTop": "0.35rem",
                }
            },
            f"Prioridad {tarea.prioridad.value}",
        ),
        html.div(
            {"style": {"marginTop": "0.5rem"}},
            [
                html.button(
                    {
                        "key": destino.value,
                        "type": "button",
                        "style": ESTILO_BOTON,
                        "on_click": lambda evento, destino=destino: manejar_clic(
                            evento, destino
                        ),
                    },
                    f"→ {destino.value}",
                )
                for destino in COLUMNAS
                if destino is not tarea.estado
            ],
        ),
    )


@component
def columna_kanban(
    estado: EstadoTarea,
    tareas: list[Tarea],
    integrantes: dict[int, str],
    al_transicionar,
):
    return html.div(
        {"style": ESTILO_COLUMNA},
        html.h3(
            {"style": {"margin": "0 0 0.75rem 0", "fontSize": "1rem"}},
            f"{estado.value} ({len(tareas)})",
        ),
        [
            tarjeta_tarea(
                tarea=tarea,
                integrantes=integrantes,
                al_transicionar=al_transicionar,
                key=str(tarea.id),
            )
            for tarea in tareas
        ]
        or [
            html.p(
                {"style": {"fontSize": "0.8rem", "color": "#718096"}},
                "Sin tareas",
            )
        ],
    )


@component
def panel_edt(tareas: list[Tarea]):
    grupos = _agrupar_por_entregable(tareas)

    if not grupos:
        contenido = [html.p({"style": {"margin": 0}}, "Sin entregables registrados")]
    else:
        contenido = [
            html.div(
                {"key": str(entregable_id), "style": {"marginBottom": "0.5rem"}},
                html.strong(f"Entregable #{entregable_id}"),
                html.span(
                    {"style": {"color": "#718096", "fontSize": "0.8rem"}},
                    f" — {len(tareas_entregable)} tarea(s)",
                ),
                html.ul(
                    {"style": {"margin": "0.25rem 0 0 1.25rem", "padding": 0}},
                    [
                        html.li(
                            {"key": str(tarea.id), "style": {"fontSize": "0.85rem"}},
                            f"{tarea.titulo} · {tarea.estado.value}",
                        )
                        for tarea in tareas_entregable
                    ],
                ),
            )
            for entregable_id, tareas_entregable in grupos.items()
        ]

    return html.div(
        {"style": ESTILO_PANEL},
        html.h3(
            {"style": {"margin": "0 0 0.5rem 0", "fontSize": "1rem"}},
            "Desglose EDT",
        ),
        contenido,
    )


@component
def tablero_kanban(
    tareas_iniciales: Iterable[Tarea],
    db_path: str | Path,
    integrantes: Iterable[Integrante] = (),
):
    tareas, set_tareas = hooks.use_state(list(tareas_iniciales))
    mensaje_error, set_mensaje_error = hooks.use_state("")
    mapa_integrantes = _mapa_integrantes(integrantes)

    def al_transicionar(tarea: Tarea, nuevo_estado: EstadoTarea):
        match validar_y_cambiar_estado(tarea, nuevo_estado):
            case Ok(tarea_actualizada):
                try:
                    actualizar_estado_tarea(
                        tarea.id, tarea_actualizada.estado.value, db_path
                    )
                except Exception as error:
                    set_mensaje_error(
                        f"No se pudo guardar el cambio en la base de datos: {error}"
                    )
                    return

                set_tareas(
                    lambda actuales: [
                        tarea_actualizada if actual.id == tarea.id else actual
                        for actual in actuales
                    ]
                )
                set_mensaje_error("")
            case Err(error):
                set_mensaje_error(error)

    hijos = [panel_edt(tareas=tareas, key="panel-edt")]

    if mensaje_error:
        hijos.append(
            html.div(
                {
                    "key": "mensaje-error",
                    "role": "alert",
                    "style": {
                        "backgroundColor": "#fed7d7",
                        "color": "#822727",
                        "borderRadius": "8px",
                        "padding": "0.5rem 0.75rem",
                        "marginBottom": "1rem",
                    },
                },
                mensaje_error,
            )
        )

    hijos.append(
        html.div(
            {"key": "tablero", "style": ESTILO_TABLERO},
            [
                columna_kanban(
                    estado=estado,
                    tareas=[tarea for tarea in tareas if tarea.estado is estado],
                    integrantes=mapa_integrantes,
                    al_transicionar=al_transicionar,
                    key=estado.value,
                )
                for estado in COLUMNAS
            ],
        )
    )

    return html.div(hijos)
