
"""
Nodos de ejecución de LangGraph para el asistente de Picanteo.

Cada nodo recibe el estado compartido y devuelve únicamente
las actualizaciones que deben aplicarse al grafo.
"""

from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from chains.response_chain import crear_respuesta_chain
from chains.router_chain import crear_router_chain
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.retrieval import recuperar_documentos
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


def _seleccionar_contexto(
    state: BusinessState,
    max_interacciones: int = 2,
) -> list:
    """
    Selecciona las últimas interacciones completas.

    Una interacción empieza con HumanMessage y conserva
    todos los mensajes posteriores hasta la siguiente
    pregunta del usuario.

    No modifica el historial original del checkpointer.
    """

    mensajes = state.get("messages", [])

    grupos = []
    grupo_actual = []

    for mensaje in mensajes:
        if getattr(mensaje, "type", "") == "human":
            if grupo_actual:
                grupos.append(grupo_actual)
            grupo_actual = [mensaje]
        elif grupo_actual:
            grupo_actual.append(mensaje)

    if grupo_actual:
        grupos.append(grupo_actual)

    seleccionados = grupos[-max_interacciones:]

    return [
        mensaje
        for grupo in seleccionados
        for mensaje in grupo
    ]


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
        "herramientas_usadas": [],
        "pasos_ejecutados": ["enrutador"],
        "documentos_recuperados": [],
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
        SystemMessage(
            content=_construir_system_prompt(state)
        ),
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


def rag_node(state: BusinessState) -> dict:
    """Recupera información documental y responde con Gemini."""

    pregunta = _obtener_pregunta(state)


    # Recuperar contexto reciente de la conversación.
    historial = state.get("messages", [])

    preguntas_recientes = [
        mensaje.content
        for mensaje in historial
        if getattr(mensaje, "type", "") == "human"
        and isinstance(mensaje.content, str)
    ]

    # Combinar las últimas dos preguntas para resolver
    # referencias como "esa recomendación".
    
    consulta_recuperacion = " ".join(
        preguntas_recientes[-2:]
    )

    referencias_anteriores = (
        "esa recomendación",
        "esa recomendacion",
        "lo anterior",
        "esa información",
        "esa informacion",
        "lo que mencionaste",
    )

    pregunta_normalizada = pregunta.lower()

    if (
        len(preguntas_recientes) >= 2
        and any(
            referencia in pregunta_normalizada
            for referencia in referencias_anteriores
        )
    ):
        consulta_recuperacion = preguntas_recientes[-2]


    documentos = recuperar_documentos(
        consulta_recuperacion,
        limite=2,
    )


    if not documentos:
        respuesta = (
            "No encontré información suficiente en la "
            "guía operativa de Picanteo para responder "
            "esta consulta."
        )

    else:
        contexto = "\n\n".join(
            f"Fuente: {doc['fuente']}\n"
            f"Sección: {doc['titulo']}\n"
            f"Contenido:\n{doc['contenido']}"
            for doc in documentos
        )

        modelo = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
        )

        mensajes = [
            SystemMessage(
                content=(
                    "Eres el asistente documental de Picanteo. "
                    "Responde únicamente con información "
                    "sustentada en el contexto recuperado. "
                    "No inventes procedimientos ni datos reales. "
                    "Si la información es insuficiente, indícalo. "
                    "Menciona el documento y la sección utilizada. "
                    "Si el usuario hace referencia a una recomendación, "
                    "respuesta o tema anterior mediante expresiones como "
                    "'esa recomendación', 'eso' o 'lo anterior', utiliza "
                    "el historial conversacional para identificar el referente. "
                    "Si la fuente documental recuperada permite responder, "
                    "menciona su sección exacta y no pidas aclaraciones "
                    "innecesarias. No inventes fuentes ni secciones. "
                    "Responde en español.\n\n"
                    f"CONTEXTO DOCUMENTAL:\n{contexto}"
                )
            ),
            *state.get("messages", [])[-3:],
        ]

        respuesta_modelo = modelo.invoke(mensajes)

        respuesta = respuesta_modelo.content

    return {
        "messages": [AIMessage(content=respuesta)],
        "documentos_recuperados": documentos,
        "pasos_ejecutados": [
            *state.get("pasos_ejecutados", []),
            "rag",
        ],
    }
