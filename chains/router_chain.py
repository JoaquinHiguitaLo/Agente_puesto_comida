from prompts.negocio_prompt import ROUTER_SYSTEM_PROMPT

"""Chain de clasificación para decidir entre Chain y Agent."""


from typing import Literal

from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

from prompts.negocio_prompt import ROUTER_SYSTEM_PROMPT


class RutaConsulta(BaseModel):
    """Ruta seleccionada para atender la solicitud."""

    ruta: Literal["chain", "agent"] = Field(
        description=(
            "Usa 'chain' para consultas generales que no requieren "
            "herramientas y 'agent' cuando se necesitan datos del "
            "negocio o herramientas."
        )
    )

    motivo: str = Field(
        description="Justificación breve de la selección de la ruta."
    )


def crear_router_chain():
    """Crea la Chain que clasifica la solicitud."""

    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0,
    )

    structured_model = model.with_structured_output(RutaConsulta)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "{pregunta}"),
        ]
    )

    return prompt | structured_model