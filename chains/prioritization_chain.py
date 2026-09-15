"""Chain para priorizar información conocida del negocio."""

import json

from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import ChatPromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


def crear_priorizacion_chain():
    """Crea una Chain fija: datos -> prompt -> modelo -> salida."""

    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                Prioriza información del negocio usando exclusivamente
                los datos proporcionados.

                Considera los valores, cantidades, niveles de stock,
                importancia y contexto registrado.

                No inventes información.

                Devuelve una lista numerada breve con la justificación
                de cada prioridad.
                """.strip(),
            ),
            (
                "human",
                "Información disponible:\n{datos}\n\n"
                "Contexto adicional: {contexto}",
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def serializar_datos(datos) -> str:
    """Convierte los datos a JSON legible para la Chain."""

    return json.dumps(
        datos,
        ensure_ascii=False,
        indent=2,
    )