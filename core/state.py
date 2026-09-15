"""Gestión de estado, memoria y trazabilidad del agente."""

import streamlit as st


# Estado inicial del negocio.
NEGOCIO_INICIAL = {
    "nombre_puesto": "",
}


def inicializar_estado() -> None:
    """Inicializa el estado persistente de la sesión."""

    # Información básica del negocio.
    if "contexto_negocio" not in st.session_state:
        st.session_state.contexto_negocio = NEGOCIO_INICIAL.copy()

    # Memoria de la conversación.
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    # Información de la última ejecución del agente.
    if "ultima_ejecucion" not in st.session_state:
        st.session_state.ultima_ejecucion = {
            "ruta": "Sin ejecución",
            "motivo": "",
            "tools": [],
            "ultima_consulta": "Ninguna",
            "ultima_herramienta": "Ninguna",
        }


def agregar_mensaje(rol: str, contenido: str) -> None:
    """Agrega un mensaje a la memoria de la conversación."""

    st.session_state.mensajes.append(
        {
            "rol": rol,
            "contenido": contenido,
        }
    )


def obtener_memoria(limite: int = 6) -> list:
    """Obtiene los mensajes más recientes de la conversación."""

    return st.session_state.mensajes[-limite:]


def obtener_contexto_negocio() -> dict:
    """Obtiene la información básica del negocio."""

    return st.session_state.contexto_negocio


def obtener_estado_agente() -> dict:
    """Obtiene la información de trazabilidad de la última ejecución."""

    return st.session_state.ultima_ejecucion


def actualizar_estado(
    nombre_puesto: str | None = None,
    ultima_consulta: str | None = None,
    ultima_herramienta: str | None = None,
) -> None:
    """Actualiza el contexto del negocio y la trazabilidad del agente."""

    # Actualizar información del negocio.
    if nombre_puesto:
        st.session_state.contexto_negocio["nombre_puesto"] = (
            nombre_puesto
        )

    # Registrar la última consulta realizada por el usuario.
    if ultima_consulta:
        st.session_state.ultima_ejecucion["ultima_consulta"] = (
            ultima_consulta
        )

    # Registrar la última herramienta utilizada por el agente.
    if ultima_herramienta:
        st.session_state.ultima_ejecucion["ultima_herramienta"] = (
            ultima_herramienta
        )

        st.session_state.ultima_ejecucion["tools"] = [
            ultima_herramienta
        ]


def reiniciar_estado() -> None:
    """Reinicia memoria, contexto del negocio y trazabilidad."""

    st.session_state.mensajes = []

    st.session_state.contexto_negocio = NEGOCIO_INICIAL.copy()

    st.session_state.ultima_ejecucion = {
        "ruta": "Sin ejecución",
        "motivo": "",
        "tools": [],
        "ultima_consulta": "Ninguna",
        "ultima_herramienta": "Ninguna",
    }