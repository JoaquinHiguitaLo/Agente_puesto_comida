"""Lógica principal del agente de IA para la gestión del puesto de comida."""

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from core.state import (
    obtener_memoria,
    obtener_contexto_negocio,
)
from tools.ventas_tool import consultar_ventas


# Cliente para comunicarse con Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


def construir_contexto() -> str:
    """Construye las instrucciones y el contexto que recibe el modelo."""

    contexto_negocio = obtener_contexto_negocio()
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

    contexto = construir_contexto()

    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=mensaje_usuario,
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[consultar_ventas],
        ),
    )

    return respuesta.text