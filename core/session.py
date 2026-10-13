
"""
Gestión de sesiones de LangGraph para negocios pequeños.

Este módulo conecta la sesión de Streamlit con el checkpointer
del grafo para mantener separado el estado de cada conversación.
"""

import uuid

import streamlit as st

from graph.workflow import crear_grafo


# ============================================================
# 1. OBTENER EL GRAFO
# ============================================================

@st.cache_resource
def obtener_grafo():
    """
    Crea el grafo una sola vez por proceso de Streamlit.

    Es importante reutilizar la misma instancia: si creáramos
    un grafo nuevo en cada pregunta, también crearíamos un
    MemorySaver nuevo y perderíamos el acceso a sus checkpoints.
    """

    return crear_grafo()


# ============================================================
# 2. IDENTIFICAR LA CONVERSACIÓN
# ============================================================

def inicializar_thread_id() -> str:
    """
    Asigna un identificador único a la sesión de Streamlit.

    El mismo identificador se conserva durante los reruns
    normales de la aplicación.
    """

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    return st.session_state.thread_id


# ============================================================
# 3. CONFIGURAR EL CHECKPOINTER
# ============================================================

def obtener_configuracion_grafo() -> dict:
    """
    Devuelve la configuración que LangGraph necesita para
    localizar el estado de la conversación actual.
    """

    thread_id = inicializar_thread_id()

    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


# ============================================================
# 4. EJECUTAR EL GRAFO
# ============================================================

def invocar_grafo(estado_inicial: dict) -> dict:
    """
    Ejecuta el grafo utilizando el identificador de la sesión.

    El checkpointer recupera el estado asociado a ese hilo
    y guarda el nuevo checkpoint al avanzar la ejecución.
    """

    grafo = obtener_grafo()
    config = obtener_configuracion_grafo()

    return grafo.invoke(
        estado_inicial,
        config=config,
    )


# ============================================================
# 5. INICIAR UNA CONVERSACIÓN NUEVA
# ============================================================

def crear_nueva_sesion_grafo() -> str:
    """
    Asigna un nuevo identificador para empezar una conversación
    independiente de la anterior.
    """

    st.session_state.thread_id = str(uuid.uuid4())

    return st.session_state.thread_id
