"""Gestión de estado, memoria y trazabilidad del agente."""

import re

import streamlit as st


# ============================================================
# ESTADO INICIAL DEL NEGOCIO
# ============================================================

NEGOCIO_INICIAL = {
    "nombre_puesto": "",
}


# ============================================================
# INICIALIZAR ESTADO
# ============================================================

def inicializar_estado() -> None:
    """Inicializa el estado persistente de la sesión."""

    if "contexto_negocio" not in st.session_state:
        st.session_state.contexto_negocio = NEGOCIO_INICIAL.copy()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if "ultima_ejecucion" not in st.session_state:
        st.session_state.ultima_ejecucion = {
            "ruta": "Sin ejecución",
            "motivo": "",
            "tools": [],
        }


# ============================================================
# ACTUALIZAR CONTEXTO DEL NEGOCIO
# ============================================================

def actualizar_contexto_negocio(texto: str) -> None:
    """
    Extrae información explícita sobre el nombre del puesto
    y la guarda en el estado de la sesión.
    """

    patrones_nombre = [
        r"(?:mi puesto de comida|mi puesto|mi negocio)"
        r"\s+se llama\s+([A-Za-zÁÉÍÓÚáéíóúÑñ0-9_-]+)"
    ]

    for patron in patrones_nombre:

        coincidencia = re.search(
            patron,
            texto,
            re.IGNORECASE,
        )

        if coincidencia:

            nombre = coincidencia.group(1).strip()

            st.session_state.contexto_negocio[
                "nombre_puesto"
            ] = nombre.capitalize()

            break


# ============================================================
# MEMORIA DE CONVERSACIÓN
# ============================================================

def agregar_mensaje(
    rol: str,
    contenido: str,
) -> None:
    """Agrega un mensaje a la memoria de la conversación."""

    st.session_state.mensajes.append(
        {
            "rol": rol,
            "contenido": contenido,
        }
    )


def obtener_memoria(limite: int = 6) -> str:
    """
    Obtiene los últimos mensajes de la conversación
    como texto para enviarlos al Agent.
    """

    mensajes = st.session_state.mensajes[-limite:]

    return "\n".join(
        f"{mensaje['rol']}: {mensaje['contenido']}"
        for mensaje in mensajes
    )


# ============================================================
# CONTEXTO DEL NEGOCIO
# ============================================================

def obtener_contexto_negocio() -> dict:
    """Obtiene la información almacenada del negocio."""

    return st.session_state.contexto_negocio


# ============================================================
# TRAZABILIDAD DE EJECUCIÓN
# ============================================================

def registrar_ejecucion(resultado: dict) -> None:
    """
    Registra la información de la última ejecución del agente.

    Guarda:
    - Ruta utilizada.
    - Motivo de la decisión del Router.
    - Tools ejecutadas.
    """

    st.session_state.ultima_ejecucion = {
        "ruta": resultado.get(
            "ruta",
            "Desconocida",
        ),
        "motivo": resultado.get(
            "motivo",
            "",
        ),
        "tools": resultado.get(
            "tools",
            [],
        ),
    }


def obtener_estado_agente() -> dict:
    """Obtiene la información de trazabilidad."""

    return st.session_state.ultima_ejecucion


# ============================================================
# REINICIAR CONVERSACIÓN
# ============================================================

def reiniciar_estado() -> None:
    """Reinicia completamente la conversación y su trazabilidad."""

    st.session_state.mensajes = []

    st.session_state.contexto_negocio = (
        NEGOCIO_INICIAL.copy()
    )

    st.session_state.ultima_ejecucion = {
        "ruta": "Sin ejecución",
        "motivo": "",
        "tools": [],
    }