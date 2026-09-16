"""
Núcleo del Agente de puesto de comida v2 con LangChain.

Decide si una solicitud puede resolverse mediante una Chain
determinista o mediante un Agent con múltiples Tools.

La estructura sigue el patrón propuesto en la guía académica,
adaptándolo al dominio de gestión de un puesto de comida.
"""

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from chains.response_chain import crear_respuesta_chain
from chains.router_chain import crear_router_chain

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

from prompts.negocio_prompt import AGENT_SYSTEM_TEMPLATE

from tools.ventas_tool import consultar_ventas
from tools.inventario_tool import consultar_inventario
from tools.proveedores_tool import consultar_proveedores
from tools.compras_tool import consultar_compras
from tools.fecha_tool import obtener_fecha
from tools.productos_tool import consultar_productos


# ============================================================
# TOOLS DISPONIBLES PARA EL AGENTE
# ============================================================

TOOLS = [
    obtener_fecha,
    consultar_ventas,
    consultar_inventario,
    consultar_proveedores,
    consultar_compras,
    consultar_productos,
]


# ============================================================
# CREACIÓN DEL MODELO
# ============================================================

def _crear_modelo() -> ChatGoogleGenerativeAI:
    """
    Crea el modelo de lenguaje que utilizará el Agent.

    Se utiliza Gemini mediante la integración de LangChain.
    """

    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )


# ============================================================
# CONSTRUCCIÓN DEL SYSTEM PROMPT
# ============================================================

def _construir_system_prompt(
    nombre_negocio: str,
    memoria: str,
) -> str:
    """
    Construye las instrucciones principales que recibe el Agent.

    El prompt incorpora el nombre del negocio y la memoria
    reciente de la conversación.
    """

    return AGENT_SYSTEM_TEMPLATE.format(
        nombre_negocio=nombre_negocio or "No registrado",
        memoria=memoria or "Sin memoria reciente.",
    )


# ============================================================
# EXTRAER RESPUESTA FINAL
# ============================================================

def _extraer_texto_final(result: dict) -> str:
    """
    Extrae el contenido textual del último mensaje generado
    por el Agent.
    """

    mensajes = result.get("messages", [])

    if not mensajes:
        return "No fue posible generar una respuesta."

    contenido = mensajes[-1].content

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):

        partes = []

        for bloque in contenido:

            if (
                isinstance(bloque, dict)
                and bloque.get("type") == "text"
            ):
                partes.append(
                    str(bloque.get("text", ""))
                )

            elif isinstance(bloque, str):
                partes.append(bloque)

        texto = "\n".join(
            parte for parte in partes if parte
        ).strip()

        return texto or "No fue posible generar una respuesta."

    return str(contenido)


# ============================================================
# DETECTAR TOOLS UTILIZADAS
# ============================================================

def _detectar_tools_usadas(result: dict) -> list[str]:
    """
    Obtiene los nombres de las Tools que fueron solicitadas
    por el modelo durante la ejecución del Agent.
    """

    usadas: list[str] = []

    for mensaje in result.get("messages", []):

        tool_calls = getattr(
            mensaje,
            "tool_calls",
            None
        ) or []

        for call in tool_calls:

            nombre = call.get("name")

            if nombre and nombre not in usadas:
                usadas.append(nombre)

    return usadas


# ============================================================
# RESPUESTA PRINCIPAL DEL AGENTE
# ============================================================

def responder(
    mensaje_usuario: str,
    nombre_negocio: str,
    memoria: str,
) -> dict:
    """
    Procesa la solicitud del usuario.

    Primero utiliza el Router Chain para determinar si la consulta
    puede resolverse mediante una Chain determinista o si requiere
    un Agent con Tools.

    Retorna información sobre:

    - respuesta generada
    - ruta utilizada
    - motivo de la decisión
    - herramientas utilizadas
    """

    # --------------------------------------------------------
    # 1. CREAR ROUTER
    # --------------------------------------------------------

    router = crear_router_chain()

    decision = router.invoke(
        {
            "pregunta": mensaje_usuario
        }
    )

    # --------------------------------------------------------
    # 2. EJECUTAR CHAIN DETERMINISTA
    # --------------------------------------------------------

    if decision.ruta == "chain":

        chain = crear_respuesta_chain()

        texto = chain.invoke(
            {
                "pregunta": mensaje_usuario
            }
        )

        return {
            "respuesta": texto,
            "ruta": "Chain",
            "motivo": decision.motivo,
            "tools": [],
        }

    # --------------------------------------------------------
    # 3. CREAR MODELO
    # --------------------------------------------------------

    model = _crear_modelo()

    # --------------------------------------------------------
    # 4. CREAR AGENT
    # --------------------------------------------------------

    agent = create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=_construir_system_prompt(
            nombre_negocio=nombre_negocio,
            memoria=memoria,
        ),
    )

    # --------------------------------------------------------
    # 5. EJECUTAR AGENT
    # --------------------------------------------------------

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": mensaje_usuario,
                }
            ]
        }
    )

    # --------------------------------------------------------
    # 6. RETORNAR RESULTADO
    # --------------------------------------------------------

    return {
        "respuesta": _extraer_texto_final(result),
        "ruta": "Agent",
        "motivo": decision.motivo,
        "tools": _detectar_tools_usadas(result),
    }