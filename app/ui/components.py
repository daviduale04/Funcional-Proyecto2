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
                "padding": "20px 24px",
                "borderRadius": "12px",
                "marginBottom": "24px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.06)",
                "border": "1px solid #e2e8f0",
            }
        },
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "14px"}},
            html.span({"style": {"fontSize": "20px"}}, "📋"),
            html.h2({"style": {"margin": "0", "fontSize": "17px", "color": "#0f172a", "fontWeight": "700"}}, "Estructura de Desglose del Trabajo (EDT/WBS)")
        ),
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "16px"}},
            [
                html.div(
                    {
                        "key": str(ent.id),
                        "style": {
                            "background": "#f8fafc",
                            "padding": "14px",
                            "borderRadius": "8px",
                            "borderLeft": "4px solid #3b82f6",
                        }
                    },
                    html.div(
                        {"style": {"fontWeight": "600", "fontSize": "14px", "color": "#1e293b", "marginBottom": "4px"}},
                        f"{ent.nombre}"
                    ),
                    html.p({"style": {"margin": "0 0 10px 0", "fontSize": "12px", "color": "#64748b"}}, ent.descripcion),
                    html.ul(
                        {"style": {"margin": "0", "paddingLeft": "18px", "color": "#334155"}},
                        [
                            html.li(
                                {"key": str(t.id), "style": {"fontSize": "13px", "marginBottom": "4px"}},
                                f"{t.titulo} · ",
                                html.span(
                                    {
                                        "style": {
                                            "fontSize": "11px",
                                            "fontWeight": "600",
                                            "color": "#0284c7" if t.estado == EstadoTarea.TERMINADA else "#475569"
                                        }
                                    },
                                    t.estado.value
                                )
                            )
                            for t in agrupadas.get(ent.id, [])
                        ]
                    )
                )
                for ent in entregables
            ]
        )
    )

@component
def TarjetaTarea(tarea: Tarea, integrantes_map: dict, on_cambiar_estado, on_eliminar_tarea):
    transiciones = [
        EstadoTarea.PENDIENTE,
        EstadoTarea.EN_PROGRESO,
        EstadoTarea.EN_REVISION,
        EstadoTarea.TERMINADA,
    ]

    nombre_responsable = integrantes_map.get(tarea.responsable_id, "Sin asignar")

    color_prioridad = {
        Prioridad.ALTA: "#ef4444",
        Prioridad.MEDIA: "#f59e0b",
        Prioridad.BAJA: "#10b981",
    }.get(tarea.prioridad, "#64748b")

    return html.div(
        {
            "style": {
                "background": "#ffffff",
                "padding": "16px",
                "marginBottom": "12px",
                "borderRadius": "10px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "border": "1px solid #e2e8f0",
                "display": "flex",
                "flexDirection": "column",
                "position": "relative",
            }
        },
        # Botón Eliminar en la esquina superior
        html.button(
            {
                "style": {
                    "position": "absolute",
                    "top": "12px",
                    "right": "12px",
                    "background": "transparent",
                    "border": "none",
                    "cursor": "pointer",
                    "color": "#94a3b8",
                    "fontSize": "14px",
                },
                "title": "Eliminar tarea",
                "on_click": lambda e: on_eliminar_tarea(tarea.id),
            },
            "✕"
        ),
        html.h4({"style": {"margin": "0 0 6px 0", "fontSize": "14px", "color": "#0f172a", "paddingRight": "20px"}}, tarea.titulo),
        tarea.descripcion and html.p({"style": {"margin": "0 0 10px 0", "color": "#64748b", "fontSize": "12px"}}, tarea.descripcion),
        html.div(
            {"style": {"fontSize": "12px", "color": "#475569", "marginBottom": "10px"}},
            f"👤 {nombre_responsable}"
        ),
        html.div(
            {"style": {"marginBottom": "12px"}},
            html.span(
                {
                    "style": {
                        "background": color_prioridad,
                        "color": "#ffffff",
                        "fontSize": "10px",
                        "fontWeight": "700",
                        "padding": "3px 8px",
                        "borderRadius": "12px",
                        "textTransform": "uppercase",
                    }
                },
                tarea.prioridad.value
            )
        ),
        html.div(
            {"style": {"display": "flex", "flexDirection": "column", "gap": "5px"}},
            [
                html.button(
                    {
                        "style": {
                            "fontSize": "11px",
                            "padding": "6px 8px",
                            "cursor": "pointer",
                            "borderRadius": "6px",
                            "border": "1px solid #cbd5e1",
                            "background": "#f8fafc",
                            "color": "#334155",
                            "textAlign": "left",
                            "transition": "all 0.15s ease",
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
def ColumnaKanban(titulo: str, tareas: list[Tarea], integrantes_map: dict, on_cambiar_estado, on_eliminar_tarea):
    return html.div(
        {
            "style": {
                "flex": "1",
                "minWidth": "260px",
                "background": "#f1f5f9",
                "borderRadius": "10px",
                "padding": "16px",
                "border": "1px solid #e2e8f0",
                "display": "flex",
                "flexDirection": "column",
            }
        },
        html.div(
            {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "14px"}},
            html.h3({"style": {"margin": "0", "fontSize": "15px", "color": "#1e293b", "fontWeight": "600"}}, titulo),
            html.span(
                {"style": {"background": "#e2e8f0", "color": "#475569", "borderRadius": "12px", "padding": "2px 8px", "fontSize": "11px", "fontWeight": "600"}},
                str(len(tareas))
            )
        ),
        html.div(
            [
                TarjetaTarea(
                    tarea=t,
                    integrantes_map=integrantes_map,
                    on_cambiar_estado=on_cambiar_estado,
                    on_eliminar_tarea=on_eliminar_tarea,
                    key=str(t.id),
                )
                for t in tareas
            ]
        ),
    )

@component
def TableroKanban():
    tareas, set_tareas = use_state(database.listar_tareas())
    entregables = database.listar_entregables()
    integrantes = database.listar_integrantes()
    mensaje_error, set_mensaje_error = use_state("")
    filtro_resp, set_filtro_resp = use_state("TODOS")

    # Estados para el formulario de nueva tarea
    nuevo_titulo, set_nuevo_titulo = use_state("")
    nuevo_desc, set_nuevo_desc = use_state("")
    nuevo_entregable, set_nuevo_entregable = use_state(str(entregables[0].id) if entregables else "1")
    nuevo_responsable, set_nuevo_responsable = use_state(str(integrantes[0].id) if integrantes else "1")
    nueva_prioridad, set_nueva_prioridad = use_state(Prioridad.MEDIA.value)

    integrantes_map = {integ.id: integ.nombre for integ in integrantes}

    def handle_cambiar_estado(tarea: Tarea, nuevo_estado: EstadoTarea):
        # 1. El Functional Core valida la regla pura
        resultado = kanban.validar_y_cambiar_estado(tarea, nuevo_estado)
        
        # 2. La Imperative Shell procesa el resultado
        match resultado:
            case Ok(tarea_actualizada):
                database.actualizar_estado_tarea_db(tarea_actualizada.id, tarea_actualizada.estado)
                set_tareas(database.listar_tareas())
                set_mensaje_error("")
            case Err(error):
                set_mensaje_error(f"Operación rechazada por el Core: {error}")

    def handle_eliminar_tarea(id_tarea: int):
        database.eliminar_tarea_db(id_tarea)
        set_tareas(database.listar_tareas())
        set_mensaje_error("")

    def handle_crear_tarea(event):
        # Valida mediante el núcleo funcional antes de persistir
        validacion = edt.validar_creacion_tarea(
            id_tarea=0,
            id_entregable=int(nuevo_entregable),
            titulo=nuevo_titulo,
            descripcion=nuevo_desc,
            prioridad=Prioridad(nueva_prioridad),
            responsable_id=int(nuevo_responsable) if nuevo_responsable else None,
        )

        match validacion:
            case Ok(tarea_valida):
                database.insertar_tarea_db(
                    id_entregable=tarea_valida.id_entregable,
                    titulo=tarea_valida.titulo,
                    descripcion=tarea_valida.descripcion,
                    responsable_id=tarea_valida.responsable_id,
                    prioridad=tarea_valida.prioridad,
                )
                set_tareas(database.listar_tareas())
                set_nuevo_titulo("")
                set_nuevo_desc("")
                set_mensaje_error("")
            case Err(error):
                set_mensaje_error(f"Validación de Tarea fallida: {error}")

    # Filtrado funcional declarativo usando Closures y HOF
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
        {"style": {"fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "padding": "32px", "background": "#f8fafc", "minHeight": "100vh"}},
        
        # Encabezado
        html.div(
            {"style": {"marginBottom": "24px"}},
            html.h1({"style": {"margin": "0 0 6px 0", "fontSize": "26px", "color": "#0f172a", "fontWeight": "800"}}, "Gestor de Proyectos: EDT & Kanban"),
            html.p({"style": {"margin": "0", "fontSize": "14px", "color": "#64748b"}}, "Arquitectura: Functional Core & Imperative Shell · ReactPy · SQLite")
        ),

        # Formulario rápido para agregar nueva tarea
        html.div(
            {
                "style": {
                    "background": "#ffffff",
                    "padding": "18px 24px",
                    "borderRadius": "12px",
                    "marginBottom": "24px",
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.06)",
                    "border": "1px solid #e2e8f0",
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "12px",
                    "alignItems": "center",
                }
            },
            html.span({"style": {"fontWeight": "700", "fontSize": "14px", "color": "#1e293b"}}, "➕ Nueva Tarea:"),
            html.input(
                {
                    "style": {"padding": "8px 12px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px", "flex": "2", "minWidth": "160px"},
                    "placeholder": "Título de la tarea...",
                    "value": nuevo_titulo,
                    "on_change": lambda e: set_nuevo_titulo(e["target"]["value"])
                }
            ),
            html.input(
                {
                    "style": {"padding": "8px 12px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px", "flex": "2", "minWidth": "160px"},
                    "placeholder": "Descripción breve...",
                    "value": nuevo_desc,
                    "on_change": lambda e: set_nuevo_desc(e["target"]["value"])
                }
            ),
            html.select(
                {
                    "style": {"padding": "8px 10px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px"},
                    "value": nuevo_entregable,
                    "on_change": lambda e: set_nuevo_entregable(e["target"]["value"])
                },
                [html.option({"key": str(ent.id), "value": str(ent.id)}, ent.nombre) for ent in entregables]
            ),
            html.select(
                {
                    "style": {"padding": "8px 10px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px"},
                    "value": nuevo_responsable,
                    "on_change": lambda e: set_nuevo_responsable(e["target"]["value"])
                },
                [html.option({"key": str(i.id), "value": str(i.id)}, i.nombre) for i in integrantes]
            ),
            html.select(
                {
                    "style": {"padding": "8px 10px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px"},
                    "value": nueva_prioridad,
                    "on_change": lambda e: set_nueva_prioridad(e["target"]["value"])
                },
                html.option({"value": Prioridad.BAJA.value}, "Baja"),
                html.option({"value": Prioridad.MEDIA.value}, "Media"),
                html.option({"value": Prioridad.ALTA.value}, "Alta"),
            ),
            html.button(
                {
                    "style": {
                        "background": "#0284c7",
                        "color": "#ffffff",
                        "padding": "8px 18px",
                        "borderRadius": "6px",
                        "border": "none",
                        "fontWeight": "600",
                        "cursor": "pointer",
                        "fontSize": "13px",
                    },
                    "on_click": handle_crear_tarea
                },
                "Guardar Tarea"
            )
        ),

        # Alerta de error
        mensaje_error and html.div(
            {
                "style": {
                    "background": "#fef2f2",
                    "border": "1px solid #f87171",
                    "color": "#991b1b",
                    "padding": "12px 16px",
                    "borderRadius": "8px",
                    "marginBottom": "20px",
                    "fontSize": "13px",
                    "fontWeight": "500",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                }
            },
            f"⚠ {mensaje_error}"
        ),

        # Sección EDT
        VistaEDT(entregables=entregables, tareas=tareas),

        # Barra de Filtro
        html.div(
            {"style": {"margin": "24px 0 16px 0", "display": "flex", "gap": "10px", "alignItems": "center"}},
            html.span({"style": {"fontSize": "14px", "fontWeight": "700", "color": "#1e293b"}}, "🔍 Filtrar por Responsable:"),
            html.select(
                {
                    "style": {"padding": "6px 12px", "borderRadius": "6px", "border": "1px solid #cbd5e1", "fontSize": "13px", "background": "#ffffff"},
                    "on_change": lambda e: set_filtro_resp(e["target"]["value"])
                },
                html.option({"value": "TODOS"}, "Mostrar todos"),
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
                    on_eliminar_tarea=handle_eliminar_tarea,
                    key=col.value,
                )
                for col in columnas
            ],
        ),
    )