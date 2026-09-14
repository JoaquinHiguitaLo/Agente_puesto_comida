"""Gestión de memoria y estado de la sesión del agente."""

import streamlit as st


def inicializar_estado() -> None:
    """Inicializa la memoria y el estado de la sesión."""

    # Memoria conversacional:
    # almacena los mensajes intercambiados entre usuario y agente.
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Estado estructurado:
    # contiene información obtenida o calculada durante la conversación.
    if "estado_agente" not in st.session_state:
        st.session_state.estado_agente = {
            "nombre_puesto": "",
            "ultima_consulta": "",
            "ultima_herramienta": "",
        }


def agregar_mensaje(rol: str, contenido: str) -> None:
    """Agrega un mensaje a la memoria de la conversación."""

    st.session_state.mensajes.append(
        {
            "rol": rol,
            "contenido": contenido,
        }
    )


def obtener_memoria() -> list:
    """Obtiene los mensajes recientes de la conversación."""

    return st.session_state.mensajes[-6:]


def obtener_estado_agente() -> dict:
    """Obtiene el estado actual del agente."""

    return st.session_state.estado_agente


def actualizar_estado(
    nombre_puesto: str | None = None,
    ultima_consulta: str | None = None,
    ultima_herramienta: str | None = None,
) -> None:
    """Actualiza los valores del estado del agente."""

    if nombre_puesto:
        st.session_state.estado_agente["nombre_puesto"] = nombre_puesto

    if ultima_consulta:
        st.session_state.estado_agente["ultima_consulta"] = ultima_consulta

    if ultima_herramienta:
        st.session_state.estado_agente["ultima_herramienta"] = (
            ultima_herramienta
        )


def reiniciar_estado() -> None:
    """Reinicia la memoria y el estado de la sesión."""

    st.session_state.mensajes = []

    st.session_state.estado_agente = {
        "nombre_puesto": "",
        "ultima_consulta": "",
        "ultima_herramienta": "",
    }