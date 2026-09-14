"""Lógica principal del agente de IA para la gestión del puesto de comida."""
import json
from google import genai
from google.genai import types


from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.state import (
    obtener_memoria,
    obtener_estado_agente,
    actualizar_estado,
)

from tools.ventas_tool import consultar_ventas


# Cliente para comunicarse con Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

#Funciones de utilidad para extraer información del mensaje del usuario y construir el contexto que se envía al modelo.

#wrapper es una función que envuelve otra función para agregar comportamiento adicional sin modificar directamente su implementación original.
def consultar_ventas_desde_agente() -> dict:
    """Ejecuta la Tool de ventas y registra su utilización en el estado."""

    resultado = consultar_ventas()

    actualizar_estado(
        ultima_herramienta="consultar_ventas"
    )

    print(
        "DEBUG - Tool ejecutada: consultar_ventas"
    )

    return resultado

#En este flujo, JSON funciona como un formato estructurado de intercambio entre el LLM y la aplicación. El LLM produce información estructurada y Python la interpreta para actualizar el estado de la sesión.
def extraer_estado_de_conversacion(mensaje_usuario: str) -> None:
    """Extrae información relevante del mensaje y actualiza el estado."""

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
        print("DEBUG - Resultado extracción:", datos)

        nombre_puesto = datos.get("nombre_puesto")

        if nombre_puesto:
            actualizar_estado(
                nombre_puesto=nombre_puesto
            )
            print(
                "DEBUG - Estado después de actualizar:",
                obtener_estado_agente()
    )

    except (json.JSONDecodeError, AttributeError):
        # Si el modelo no devuelve un JSON válido,
        # simplemente no modificamos el estado.
        pass


def construir_contexto() -> str:
    """Construye las instrucciones y el contexto que recibe el modelo."""

    estado_agente = obtener_estado_agente()
    memoria = obtener_memoria()

    nombre_puesto = estado_agente.get("nombre_puesto")

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
- consultar_ventas: consulta las ventas registradas del negocio.
  Utilízala cuando el usuario solicite información sobre ventas
  registradas.

REGLAS DE COMPORTAMIENTO:
- No inventes información sobre ventas, inventario, costos o ganancias.
- Si no tienes los datos necesarios, indícalo claramente.
- Si una pregunta requiere consultar información del negocio,
  utiliza la herramienta correspondiente cuando esté disponible.
- Puedes analizar información y generar recomendaciones.
- Las recomendaciones no representan una acción ejecutada.
- No debes realizar compras, modificar precios, publicar promociones
  ni ejecutar acciones que impliquen decisiones económicas importantes
  sin autorización del usuario.
- Explica tus respuestas de manera sencilla y directa.
"""

    return contexto


def responder(mensaje_usuario: str) -> str:
    """Procesa el mensaje del usuario y genera una respuesta."""

    # Primero analizamos el mensaje para detectar
    # información relevante que pueda actualizar el estado.
    extraer_estado_de_conversacion(mensaje_usuario)

    # Después de actualizar el estado,
    # construimos el contexto que recibirá el LLM.
    contexto = construir_contexto()

    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=mensaje_usuario,
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[consultar_ventas_desde_agente],
        ),
    )

    return respuesta.text