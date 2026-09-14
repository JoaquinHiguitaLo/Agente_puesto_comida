"""Interfaz principal del asistente inteligente para el puesto de comida."""

#Interfaz y coordinación de la aplicación Streamlit para el asistente inteligente del puesto de comida.


import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    inicializar_estado,
    agregar_mensaje,
    obtener_memoria,
    obtener_estado_agente,
    actualizar_estado,
    reiniciar_estado
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


# Panel lateral con la información básica del negocio.
with st.sidebar:
    st.header("🧠 Estado del agente")

    estado = obtener_estado_agente()

    # Información obtenida durante la conversación.
    nombre_puesto = estado.get("nombre_puesto")
    ultima_consulta = estado.get("ultima_consulta")
    ultima_herramienta = estado.get("ultima_herramienta")

    st.subheader("🏪 Negocio")
    st.write(nombre_puesto or "Aún no identificado")

    st.subheader("💬 Mensajes")
    st.write(len(st.session_state.mensajes))

    st.subheader("🔧 Última herramienta")
    st.write(ultima_herramienta or "Ninguna")

    st.subheader("❓ Última consulta")
    st.write(ultima_consulta or "Ninguna")

    st.divider()

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

    # Guardar el mensaje del usuario en la memoria.
    agregar_mensaje("user", mensaje_usuario)

    # Registrar la última consulta en el estado.
    actualizar_estado(
        ultima_consulta=mensaje_usuario
    )

    with st.chat_message("user"):
        st.markdown(mensaje_usuario)

    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                respuesta = responder(mensaje_usuario)
                st.markdown(respuesta)

                # Guardar la respuesta del asistente en la memoria.
                agregar_mensaje("assistant", respuesta)

                # Volver a ejecutar Streamlit para que el sidebar
                # muestre inmediatamente el estado actualizado.
                st.rerun()

            except Exception as error:
                st.error(
                    f"Ocurrió un error al consultar el agente: {error}"
                )