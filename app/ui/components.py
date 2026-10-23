from reactpy import component, html, use_state
from app.adapters import database
from app.core import edt, filters, kanban
from app.domain.models import EstadoTarea, Err, Ok, Tarea, Prioridad

@component
def VistaEDT(entregables, tareas):
    agrupadas = edt.agrupar_tareas_por_entregable(entregables, tareas)

    return html.div(
        {
            "style": {
                "background": "#ffffff",
                "padding": "20px",
                "borderRadius": "12px",
                "marginBottom": "24px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.05)",
                "border": "1px solid #e2e8f0",
            }
        },
        html.h2({"style": {"margin": "0 0 16px 0", "fontSize": "18px", "color": "#0f172a"}}, "Estructura de Desglose del Trabajo (EDT)"),
        [
            html.div(
                {"key": str(ent.id), "style": {"marginBottom": "14px"}},
                html.div(
                    {"style": {"fontWeight": "600", "fontSize": "15px", "color": "#1e293b", "marginBottom": "6px"}},
                    f"{ent.nombre} — ",
                    html.span({"style": {"color": "#64748b", "fontSize": "13px", "fontWeight": "normal"}}, f"{len(agrupadas.get(ent.id, []))} tarea(s)")
                ),
                html.ul(
                    {"style": {"margin": "0", "paddingLeft": "24px", "color": "#334155"}},
                    [
                        html.li(
                            {"key": str(t.id), "style": {"fontSize": "14px", "marginBottom": "4px"}},
                            f"{t.titulo} · ",
                            html.span({"style": {"color": "#64748b"}}, t.estado.value)
                        )
                        for t in agrupadas.get(ent.id, [])
                    ]
                )
            )
            for ent in entregables
        ]
    )

@component
def TarjetaTarea(tarea: Tarea, integrantes_map: dict, on_cambiar_estado):
    transiciones = [
        EstadoTarea.PENDIENTE,
        EstadoTarea.EN_PROGRESO,
        EstadoTarea.EN_REVISION,
        EstadoTarea.TERMINADA,
    ]

    nombre_responsable = integrantes_map.get(tarea.responsable_id, "Sin asignar")

    color_prioridad = {
        Prioridad.ALTA: "#dc2626",
        Prioridad.MEDIA: "#d97706",
        Prioridad.BAJA: "#16a34a",
    }.get(tarea.prioridad, "#64748b")

    return html.div(
        {
            "style": {
                "background": "#ffffff",
                "padding": "16px",
                "marginBottom": "12px",
                "borderRadius": "8px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                "border": "1px solid #e2e8f0",
            }
        },
        html.h4({"style": {"margin": "0 0 6px 0", "fontSize": "15px", "color": "#0f172a"}}, tarea.titulo),
        html.div(
            {"style": {"fontSize": "13px", "color": "#64748b", "marginBottom": "10px"}},
            f"Responsable: {nombre_responsable}"
        ),
        html.span(
            {
                "style": {
                    "display": "inline-block",
                    "background": color_prioridad,
                    "color": "#ffffff",
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "padding": "2px 8px",
                    "borderRadius": "12px",
                    "marginBottom": "14px",
                }
            },
            f"Prioridad {tarea.prioridad.value}"
        ),
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "6px"}},
            [
                html.button(
                    {
                        "style": {
                            "fontSize": "12px",
                            "padding": "6px 10px",
                            "cursor": "pointer",
                            "borderRadius": "6px",
                            "border": "1px solid #cbd5e1",
                            "background": "#ffffff",
                            "color": "#1e293b",
                            "textAlign": "left",
                        },
                        "on_click": lambda e, est=estado_dest: on_cambiar_estado(tarea, est),
                    },
                    f"→ {estado_dest.value}",
                )
                for estado_dest in transiciones
                if estado_dest != tarea.estado
            ],
        ),
    )

@component
def ColumnaKanban(titulo: str, tareas: list[Tarea], integrantes_map: dict, on_cambiar_estado):
    return html.div(
        {
            "style": {
                "flex": "1",
                "minWidth": "250px",
                "background": "#f8fafc",
                "borderRadius": "10px",
                "padding": "14px",
                "border": "1px solid #e2e8f0",
                "display": "flex",
                "flexDirection": "column",
            }
        },
        html.h3({"style": {"margin": "0 0 14px 0", "fontSize": "15px", "color": "#0f172a"}}, f"{titulo} ({len(tareas)})"),
        html.div(
            [TarjetaTarea(tarea=t, integrantes_map=integrantes_map, on_cambiar_estado=on_cambiar_estado, key=str(t.id)) for t in tareas]
        ),
    )

@component
def TableroKanban():
    tareas, set_tareas = use_state(database.listar_tareas())
    entregables = database.listar_entregables()
    integrantes = database.listar_integrantes()
    mensaje_error, set_mensaje_error = use_state("")
    filtro_resp, set_filtro_resp = use_state("TODOS")

    # Mapa de id -> nombre de integrante
    integrantes_map = {integ.id: integ.nombre for integ in integrantes}

    def handle_cambiar_estado(tarea: Tarea, nuevo_estado: EstadoTarea):
        # Núcleo funcional valida la regla
        resultado = kanban.validar_y_cambiar_estado(tarea, nuevo_estado)
        
        match resultado:
            case Ok(tarea_actualizada):
                database.actualizar_estado_tarea_db(tarea_actualizada.id, tarea_actualizada.estado)
                set_tareas(database.listar_tareas())
                set_mensaje_error("")
            case Err(error):
                set_mensaje_error(f"Operación denegada: {error}")

    # Filtrado funcional con Closures
    tareas_visibles = tareas
    if filtro_resp != "TODOS":
        predicado = filters.crear_filtro_responsable(int(filtro_resp))
        tareas_visibles = filters.aplicar_filtros_combinados(tareas, predicado)

    columnas = [
        EstadoTarea.PENDIENTE,
        EstadoTarea.EN_PROGRESO,
        EstadoTarea.EN_REVISION,
        EstadoTarea.TERMINADA,
    ]

    return html.div(
        {"style": {"fontFamily": "Segoe UI, -apple-system, sans-serif", "padding": "28px", "background": "#f1f5f9", "minHeight": "100vh"}},
        
        # Vista de Estructura de Desglose del Trabajo
        VistaEDT(entregables=entregables, tareas=tareas),

        # Mensaje de error / advertencia de transición
        mensaje_error and html.div(
            {
                "style": {
                    "background": "#fee2e2",
                    "border": "1px solid #ef4444",
                    "color": "#991b1b",
                    "padding": "12px",
                    "borderRadius": "8px",
                    "marginBottom": "16px",
                    "fontSize": "14px",
                }
            },
            f"⚠ {mensaje_error}",
        ),

        # Filtro de responsables
        html.div(
            {"style": {"marginBottom": "20px", "display": "flex", "gap": "10px", "alignItems": "center"}},
            html.span({"style": {"fontSize": "14px", "fontWeight": "600", "color": "#334155"}}, "Filtrar por Responsable:"),
            html.select(
                {
                    "style": {"padding": "6px 10px", "borderRadius": "6px", "border": "1px solid #cbd5e1"},
                    "on_change": lambda e: set_filtro_resp(e["target"]["value"])
                },
                html.option({"value": "TODOS"}, "Todos"),
                [html.option({"key": str(i.id), "value": str(i.id)}, i.nombre) for i in integrantes]
            ),
        ),

        # Columnas Kanban
        html.div(
            {"style": {"display": "flex", "gap": "16px", "alignItems": "flex-start", "overflowX": "auto"}},
            [
                ColumnaKanban(
                    titulo=col.value,
                    tareas=[t for t in tareas_visibles if t.estado == col],
                    integrantes_map=integrantes_map,
                    on_cambiar_estado=handle_cambiar_estado,
                    key=col.value,
                )
                for col in columnas
            ],
        ),
    )