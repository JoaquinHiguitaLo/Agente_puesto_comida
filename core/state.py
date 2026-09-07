"""Gestión del estado y memoria de la sesión del agente."""

import streamlit as st


def inicializar_estado() -> None:
    """Inicializa el estado de la sesión si aún no existe."""

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "contexto_negocio" not in st.session_state:
        st.session_state.contexto_negocio = {
            "nombre_puesto": "",
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


def obtener_contexto_negocio() -> dict:
    """Obtiene la información básica del negocio."""

    return st.session_state.contexto_negocio


def actualizar_contexto_negocio(
    nombre_puesto: str | None = None,
) -> None:
    """Actualiza la información básica del negocio."""

    if nombre_puesto:
        st.session_state.contexto_negocio["nombre_puesto"] = nombre_puesto


def reiniciar_estado() -> None:
    """Reinicia la memoria y el contexto de la sesión."""

    st.session_state.mensajes = []
    st.session_state.contexto_negocio = {
        "nombre_puesto": "",
    }