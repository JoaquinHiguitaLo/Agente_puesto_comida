"""Interfaz principal del asistente inteligente para el puesto de comida."""

#Interfaz y coordinación de la aplicación Streamlit para el asistente inteligente del puesto de comida.


import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    inicializar_estado,
    agregar_mensaje,
    obtener_memoria,
    reiniciar_estado,
)


# Configuración de la página
st.set_page_config(
    page_title="Asistente puesto de comida",
    page_icon="🤖",
    layout="centered",
)


# Validar configuración
try:
    validar_configuracion()
except ValueError as error:
    st.error(str(error))
    st.stop()


# Inicializa el estado persistente de la sesión de Streamlit.
inicializar_estado()


# Encabezado principal de la aplicación.
st.title("🤖 Asistente puesto de comida")
st.caption(
    "Asistente inteligente para consultar y analizar "
    "la información de tu negocio."
)


# Panel lateral con la información académica conocida del estudiante.
with st.sidebar:
    st.header("Información del negocio")
    st.write(
        "Aquí puedes registrar la información básica de tu negocio."
    )

    # Entrada para el nombre del puesto de comida
    nombre_puesto = st.text_input(
        "Nombre del puesto de comida",
        value=st.session_state.contexto_negocio.get("nombre_puesto", ""),
    )

    # Botón para reiniciar la conversación
    if st.button("🔄 Nueva conversación"):
        reiniciar_estado()
        st.rerun()


# Mostrar mensajes anteriores
for mensaje in obtener_memoria():
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])


# Entrada del usuario
mensaje_usuario = st.chat_input(
    "Escribe una pregunta sobre tu negocio..."
)


if mensaje_usuario:

    # Mostrar mensaje del usuario
    agregar_mensaje("user", mensaje_usuario)

    with st.chat_message("user"):
        st.markdown(mensaje_usuario)

    # Generar respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                respuesta = responder(mensaje_usuario)
                st.markdown(respuesta)

                # Guardar respuesta en memoria
                agregar_mensaje("assistant", respuesta)

            except Exception as error:
                st.error(
                    f"Ocurrió un error al consultar el agente: {error}"
                )