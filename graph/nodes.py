
"""
Nodos de ejecución de LangGraph para el asistente de Picanteo.

Cada nodo recibe el estado compartido y devuelve únicamente
las actualizaciones que deben aplicarse al grafo.
"""

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from chains.response_chain import crear_respuesta_chain
from chains.router_chain import crear_router_chain
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from graph.state import BusinessState
from prompts.negocio_prompt import AGENT_SYSTEM_TEMPLATE
from tools import TOOLS_NEGOCIO


# ============================================================
# CONFIGURACIÓN DEL MODELO Y LAS HERRAMIENTAS
# ============================================================

def _crear_modelo() -> ChatGoogleGenerativeAI:
    """Crea el modelo Gemini utilizado por los nodos."""

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )


# ToolNode ejecuta las herramientas solicitadas por el modelo.
_ejecutor_tools = ToolNode(TOOLS_NEGOCIO)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def _obtener_pregunta(state: BusinessState) -> str:
    """Obtiene el último mensaje del usuario del estado."""

    for mensaje in reversed(state.get("messages", [])):
        if getattr(mensaje, "type", "") == "human":
            contenido = mensaje.content

            if isinstance(contenido, str):
                return contenido

            if isinstance(contenido, list):
                partes = []

                for bloque in contenido:
                    if isinstance(bloque, dict):
                        if bloque.get("type") == "text":
                            partes.append(bloque.get("text", ""))
                    elif isinstance(bloque, str):
                        partes.append(bloque)

                return "\n".join(partes)

            return str(contenido)

    return ""


def _agregar_paso(
    state: BusinessState,
    nombre_nodo: str,
) -> list[str]:
    """Añade el nodo actual a la trazabilidad de ejecución."""

    pasos = list(state.get("pasos_ejecutados", []))
    pasos.append(nombre_nodo)
    return pasos


def _construir_system_prompt(state: BusinessState) -> str:
    """Construye las instrucciones del agente con el contexto actual."""

    return AGENT_SYSTEM_TEMPLATE.format(
        nombre_negocio=state.get("nombre_negocio") or "No registrado",
        memoria=state.get("memoria") or "Sin memoria reciente.",
    )


# ============================================================
# NODO 1: ENRUTADOR
# ============================================================

def enrutador_node(state: BusinessState) -> dict:
    """
    Clasifica la consulta como conceptual (chain) o basada
    en datos y herramientas (agent).
    """

    router = crear_router_chain()

    decision = router.invoke(
        {"pregunta": _obtener_pregunta(state)}
    )

    return {
        "ruta": decision.ruta,
        "motivo": decision.motivo,
        "pasos_ejecutados": _agregar_paso(state, "enrutador"),
    }


# ============================================================
# NODO 2: RESPUESTA CONCEPTUAL
# ============================================================

def conceptual_node(state: BusinessState) -> dict:
    """
    Responde consultas generales sin ejecutar herramientas
    del negocio.
    """

    chain = crear_respuesta_chain()

    respuesta = chain.invoke(
        {"pregunta": _obtener_pregunta(state)}
    )

    from langchain_core.messages import AIMessage

    return {
        "messages": [AIMessage(content=respuesta)],
        "pasos_ejecutados": _agregar_paso(
            state, "nodo_conceptual"
        ),
    }


# ============================================================
# NODO 3: AGENTE RAZONADOR
# ============================================================

def agente_negocio_node(state: BusinessState) -> dict:
    """
    Analiza la consulta y decide si necesita solicitar
    una o varias herramientas.

    Si solicita herramientas, LangGraph continuará hacia
    herramientas_node. Si no, la respuesta será final.
    """

    modelo = _crear_modelo()
    modelo_con_tools = modelo.bind_tools(TOOLS_NEGOCIO)

    mensajes = [
        SystemMessage(content=_construir_system_prompt(state)),
        *state.get("messages", []),
    ]

    respuesta = modelo_con_tools.invoke(mensajes)

    herramientas = list(state.get("herramientas_usadas", []))

    for llamada in getattr(respuesta, "tool_calls", []) or []:
        nombre = llamada.get("name")

        if nombre and nombre not in herramientas:
            herramientas.append(nombre)

    return {
        "messages": [respuesta],
        "herramientas_usadas": herramientas,
        "pasos_ejecutados": _agregar_paso(
            state, "agente_negocio"
        ),
    }


# ============================================================
# NODO 4: EJECUCIÓN DE HERRAMIENTAS
# ============================================================

def herramientas_node(state: BusinessState) -> dict:
    """
    Ejecuta las herramientas solicitadas mediante ToolNode.

    Las respuestas se agregan al historial y el grafo podrá
    regresar al agente para interpretar los resultados.
    """

    resultado = _ejecutor_tools.invoke(
        {"messages": state.get("messages", [])}
    )

    return {
        "messages": resultado["messages"],
        "pasos_ejecutados": _agregar_paso(
            state, "herramientas"
        ),
    }
