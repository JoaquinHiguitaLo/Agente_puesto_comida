
"""
Definición y compilación del grafo de LangGraph para Picanteo.

Responsabilidades:
- Conectar los nodos del agente.
- Definir las rutas condicionales.
- Gestionar el ciclo de ejecución de herramientas.
- Mantener memoria mediante un checkpointer.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import tools_condition

from graph.nodes import (
    agente_negocio_node,
    conceptual_node,
    enrutador_node,
    herramientas_node,
)
from graph.state import BusinessState


# ============================================================
# FUNCIONES DE ENRUTAMIENTO
# ============================================================

def decidir_ruta(state: BusinessState) -> str:
    """Selecciona la ruta según la decisión del enrutador."""

    if state.get("ruta") == "chain":
        return "conceptual"

    return "agente"


def decidir_si_hay_herramientas(state: BusinessState) -> str:
    """
    Comprueba si el último mensaje del agente solicita herramientas.

    Si existen llamadas, el grafo pasa a ToolNode.
    Si no existen, la ejecución termina.
    """

    return tools_condition(state)


# ============================================================
# CONSTRUCCIÓN DEL GRAFO
# ============================================================

def crear_grafo():
    """Construye y compila el flujo de ejecución de Picanteo."""

    constructor = StateGraph(BusinessState)

    # Registrar los nodos.
    constructor.add_node("enrutador", enrutador_node)
    constructor.add_node("conceptual", conceptual_node)
    constructor.add_node("agente", agente_negocio_node)
    constructor.add_node("herramientas", herramientas_node)

    # Inicio -> enrutador.
    constructor.add_edge(START, "enrutador")

    # El enrutador decide entre la ruta conceptual y el agente.
    constructor.add_conditional_edges(
        "enrutador",
        decidir_ruta,
        {
            "conceptual": "conceptual",
            "agente": "agente",
        },
    )

    # La ruta conceptual termina después de responder.
    constructor.add_edge("conceptual", END)

    # El agente solicita herramientas o produce una respuesta final.
    constructor.add_conditional_edges(
        "agente",
        decidir_si_hay_herramientas,
        {
            "tools": "herramientas",
            END: END,
        },
    )

    # Después de ejecutar herramientas, vuelve al agente.
    constructor.add_edge("herramientas", "agente")

    # Checkpointer en memoria para conservar el estado por sesión.
    memoria = MemorySaver()

    return constructor.compile(checkpointer=memoria)
