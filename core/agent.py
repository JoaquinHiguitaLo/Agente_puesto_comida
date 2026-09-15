"""Lógica principal del agente de IA para la gestión del puesto de comida."""

import json

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

from core.state import (
    obtener_memoria,
    obtener_contexto_negocio,
    obtener_estado_agente,
    actualizar_estado,
)

from tools.ventas_tool import consultar_ventas


# ============================================================
# CLIENTE DE GEMINI
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# TOOL: CONSULTAR VENTAS
# ============================================================

def consultar_ventas_desde_agente() -> dict:
    """
    Ejecuta la herramienta de ventas y registra su utilización
    en el estado del agente.
    """

    resultado = consultar_ventas.invoke({})

    actualizar_estado(
        ultima_herramienta="consultar_ventas"
    )

    print(
        "DEBUG - Tool ejecutada: consultar_ventas"
    )

    return resultado


# ============================================================
# EXTRACCIÓN DE INFORMACIÓN DEL NEGOCIO
# ============================================================

def extraer_estado_de_conversacion(mensaje_usuario: str) -> None:
    """
    Extrae información relevante del mensaje del usuario
    y actualiza el estado de la sesión.
    """

    prompt = f"""
Analiza el siguiente mensaje del usuario y determina si contiene
información explícita sobre el nombre de su negocio.

MENSAJE DEL USUARIO:
{mensaje_usuario}

Reglas:
- Extrae el nombre únicamente si el usuario lo proporciona de forma clara.
- No inventes información.
- Si el usuario no proporciona el nombre del negocio, devuelve null.
- Responde únicamente con un objeto JSON válido.
- Utiliza exactamente esta estructura:

{{
    "nombre_puesto": "nombre encontrado o null"
}}
"""

    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    try:
        datos = json.loads(respuesta.text)

        print(
            "DEBUG - Resultado extracción:",
            datos
        )

        nombre_puesto = datos.get("nombre_puesto")

        if nombre_puesto:
            actualizar_estado(
                nombre_puesto=nombre_puesto
            )

            print(
                "DEBUG - Estado después de actualizar:",
                obtener_contexto_negocio()
            )

    except (json.JSONDecodeError, AttributeError):
        pass


# ============================================================
# CONTEXTO DEL AGENTE
# ============================================================

def construir_contexto() -> str:
    """
    Construye las instrucciones y el contexto que recibe Gemini.
    """

    contexto_negocio = obtener_contexto_negocio()
    estado_agente = obtener_estado_agente()
    memoria = obtener_memoria()

    nombre_puesto = contexto_negocio.get("nombre_puesto")

    contexto = f"""
Eres un asistente inteligente especializado en la gestión
de un pequeño puesto de comida.

Tu función es ayudar al propietario o administrador a analizar
la información de su negocio y tomar mejores decisiones.

Debes ser claro, preciso y práctico.

CONTEXTO DEL NEGOCIO:
- Nombre del puesto: {nombre_puesto or "No registrado"}

MEMORIA RECIENTE DE LA CONVERSACIÓN:
{memoria}

ESTADO ACTUAL DEL AGENTE:
{estado_agente}

HERRAMIENTAS DISPONIBLES:

1. consultar_ventas
   Consulta todas las ventas registradas del negocio.

   Debes utilizar esta herramienta cuando el usuario solicite:
   - sus ventas
   - ventas registradas
   - historial de ventas
   - productos vendidos
   - cantidades vendidas
   - información relacionada con las ventas

REGLAS DE COMPORTAMIENTO:

- No inventes información sobre ventas, inventario, costos o ganancias.
- Si necesitas información registrada en el sistema, utiliza la
  herramienta correspondiente.
- Puedes analizar la información obtenida mediante las herramientas.
- Puedes generar recomendaciones.
- Las recomendaciones no representan una acción ejecutada.
- No debes realizar compras, modificar precios, publicar promociones
  ni ejecutar acciones económicas importantes sin autorización.
- Si no existen datos suficientes, indícalo claramente.
- Responde de manera sencilla y directa.
"""

    return contexto


# ============================================================
# DEFINICIÓN DE LA TOOL PARA GEMINI
# ============================================================

def obtener_tool_ventas():
    """
    Define formalmente la herramienta que Gemini puede solicitar.
    """

    funcion = types.FunctionDeclaration(
        name="consultar_ventas",
        description=(
            "Consulta todas las ventas registradas del puesto "
            "de comida en el sistema."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {},
        },
    )

    return types.Tool(
        function_declarations=[funcion]
    )


# ============================================================
# RESPUESTA DEL AGENTE
# ============================================================

def responder(mensaje_usuario: str) -> str:
    """
    Procesa el mensaje del usuario, permite que Gemini decida
    si necesita utilizar una herramienta y devuelve la respuesta final.
    """

    # --------------------------------------------------------
    # 1. Extraer información del mensaje
    # --------------------------------------------------------

    extraer_estado_de_conversacion(mensaje_usuario)

    # --------------------------------------------------------
    # 2. Construir contexto
    # --------------------------------------------------------

    contexto = construir_contexto()

    # --------------------------------------------------------
    # 3. Definir la herramienta disponible
    # --------------------------------------------------------

    tool_ventas = obtener_tool_ventas()

    # --------------------------------------------------------
    # 4. Construir mensaje del usuario
    # --------------------------------------------------------

    mensaje_usuario_content = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=mensaje_usuario
            )
        ],
    )

    # --------------------------------------------------------
    # 5. Primera llamada al modelo
    # --------------------------------------------------------

    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            mensaje_usuario_content
        ],
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[tool_ventas],
        ),
    )

    # --------------------------------------------------------
    # 6. Comprobar si Gemini solicitó una herramienta
    # --------------------------------------------------------

    if not respuesta.function_calls:
        return respuesta.text

    # --------------------------------------------------------
    # 7. Obtener la llamada solicitada por Gemini
    # --------------------------------------------------------

    llamada = respuesta.function_calls[0]

    print(
        "DEBUG - Gemini solicitó:",
        llamada.name
    )

    # --------------------------------------------------------
    # 8. Ejecutar la herramienta solicitada
    # --------------------------------------------------------

    if llamada.name == "consultar_ventas":

        resultado_tool = consultar_ventas_desde_agente()

    else:

        return (
            "El agente solicitó una herramienta que "
            "no está disponible actualmente."
        )

    # --------------------------------------------------------
    # 9. Convertir el resultado de Python en respuesta
    #    para Gemini
    # --------------------------------------------------------

    respuesta_tool = types.Part.from_function_response(
        name=llamada.name,
        response={
            "result": resultado_tool
        },
    )

    contenido_tool = types.Content(
        role="user",
        parts=[
            respuesta_tool
        ],
    )

    # --------------------------------------------------------
    # 10. Segunda llamada a Gemini
    # --------------------------------------------------------
    # Gemini recibe:
    # - la pregunta original
    # - su propia solicitud de herramienta
    # - el resultado de la herramienta
    #
    # Con esto puede construir la respuesta final.

    respuesta_final = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[
            mensaje_usuario_content,
            respuesta.candidates[0].content,
            contenido_tool,
        ],
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[tool_ventas],
        ),
    )

    return respuesta_final.text