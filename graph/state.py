
"""
Esquema de estado compartido por los nodos de LangGraph.

Define la información que puede circular durante la ejecución
del asistente de gestión de Picanteo.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class BusinessState(TypedDict, total=False):
    """
    Estado compartido del agente.

    total=False permite que el estado se construya gradualmente:
    no todos los campos tienen que estar presentes desde el inicio.
    """

    # Historial de mensajes. add_messages permite agregar mensajes
    # nuevos y actualizar los existentes según su identificador.
    messages: Annotated[list[AnyMessage], add_messages]

    # Ruta seleccionada por el enrutador: "chain" o "agent".
    ruta: str

    # Explicación de por qué se seleccionó esa ruta.
    motivo: str

    # Nombres de las herramientas utilizadas durante la ejecución.
    herramientas_usadas: list[str]

    # Secuencia de nodos recorridos por el grafo.
    pasos_ejecutados: list[str]

    # Contexto del negocio y memoria textual disponible para el agente.
    nombre_negocio: str
    memoria: str
