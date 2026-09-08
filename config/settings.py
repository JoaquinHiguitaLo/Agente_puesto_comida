"""
Configuración de variables de entorno para la API de Gemini.

Este módulo carga las variables definidas en el archivo `.env` y 
proporciona la configuración necesaria para interactuar con la API de Gemini.
"""

"""Carga herramientas para leer variable de entorno"""
import os
from dotenv import load_dotenv

"""Busca el archivo .env y carga sus variables"""
load_dotenv()

"""Toma la API Key de Gemini desde las variables de entorno"""
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

"""Define el modelo de Gemini a utilizar"""
GEMINI_MODEL = "gemini-3.5-flash-lite"

"""Comprueba que realmente exista una API Key"""
def validar_configuracion() -> None:
    """Valida que la configuración necesaria para Gemini sea correcta.

    Raises:
        ValueError: Si `GEMINI_API_KEY` no está definida o conserva el valor
            de ejemplo.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY_AQUI":
        raise ValueError(
            "Configura una API Key válida en el archivo .env "
            "usando GEMINI_API_KEY."
        )