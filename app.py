"""Interfaz principal del asistente inteligente para el puesto de comida.

Este módulo coordina:
- La interfaz de Streamlit.
- El estado y memoria de la conversación.
- La identificación del negocio.
- La ejecución del Router + Chain/Agent.
- La trazabilidad de la ejecución.
"""

import streamlit as st

from config.settings import validar_configuracion
from core.agent import responder
from core.state import (
    inicializar_estado,
    agregar_mensaje,
    obtener_memoria,
    obtener_contexto_negocio,
    obtener_estado_agente,
    registrar_ejecucion,
    reiniciar_estado,
    actualizar_contexto_negocio,
)


# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Asistente puesto de comida",
    page_icon="🤖",
    layout="centered",
)


# ============================================================
# VALIDAR CONFIGURACIÓN
# ============================================================

try:
    validar_configuracion()

except ValueError as error:
    st.error(str(error))
    st.stop()


# ============================================================
# INICIALIZAR ESTADO
# ============================================================

inicializar_estado()


# ============================================================
# ENCABEZADO
# ============================================================

st.title("🤖 Asistente puesto de comida")

st.caption(
    "Asistente inteligente para consultar y analizar "
    "la información de tu negocio."
)


# ============================================================
# PANEL LATERAL
# ============================================================

with st.sidebar:

    st.header("🧠 Estado del agente")

    contexto_negocio = obtener_contexto_negocio()
    estado = obtener_estado_agente()

    nombre_puesto = contexto_negocio.get(
        "nombre_puesto",
        ""
    )

    ruta = estado.get(
        "ruta",
        "Sin ejecución"
    )

    motivo = estado.get(
        "motivo",
        ""
    )

    tools = estado.get(
        "tools",
        []
    )


    # --------------------------------------------------------
    # NEGOCIO
    # --------------------------------------------------------

    st.subheader("🏪 Negocio")

    st.write(
        nombre_puesto or "Aún no identificado"
    )


    # --------------------------------------------------------
    # MENSAJES
    # --------------------------------------------------------

    st.subheader("💬 Mensajes")

    st.write(
        len(st.session_state.mensajes)
    )


    # --------------------------------------------------------
    # ÚLTIMA EJECUCIÓN
    # --------------------------------------------------------

    st.subheader("⚙️ Última ejecución")

    st.write(ruta)


    # --------------------------------------------------------
    # MOTIVO DEL ROUTER
    # --------------------------------------------------------

    st.subheader("🧭 Motivo")

    st.write(
        motivo or "Sin información"
    )


    # --------------------------------------------------------
    # TOOLS UTILIZADAS
    # --------------------------------------------------------

    st.subheader("🔧 Tools utilizadas")

    if tools:

        for tool in tools:
            st.write(f"• {tool}")

    else:

        st.write("Ninguna")


    st.divider()


    # --------------------------------------------------------
    # NUEVA CONVERSACIÓN
    # --------------------------------------------------------

    if st.button("🔄 Nueva conversación"):

        reiniciar_estado()

        st.rerun()


# ============================================================
# MOSTRAR HISTORIAL DE CONVERSACIÓN
# ============================================================

for mensaje in st.session_state.mensajes:

    with st.chat_message(
        mensaje["rol"]
    ):

        st.markdown(
            mensaje["contenido"]
        )


# ============================================================
# ENTRADA DEL USUARIO
# ============================================================

mensaje_usuario = st.chat_input(
    "Escribe una pregunta sobre tu negocio..."
)


# ============================================================
# PROCESAMIENTO DE LA CONSULTA
# ============================================================

if mensaje_usuario:

    # --------------------------------------------------------
    # 1. ACTUALIZAR CONTEXTO DEL NEGOCIO
    # --------------------------------------------------------

    actualizar_contexto_negocio(
        mensaje_usuario
    )


    # --------------------------------------------------------
    # 2. GUARDAR MENSAJE DEL USUARIO
    # --------------------------------------------------------

    agregar_mensaje(
        "user",
        mensaje_usuario
    )


    # --------------------------------------------------------
    # 3. OBTENER CONTEXTO ACTUAL
    # --------------------------------------------------------

    contexto_negocio = obtener_contexto_negocio()

    nombre_puesto = contexto_negocio.get(
        "nombre_puesto",
        ""
    )


    # --------------------------------------------------------
    # 4. OBTENER MEMORIA RECIENTE
    # --------------------------------------------------------

    memoria = obtener_memoria()


    # --------------------------------------------------------
    # 5. MOSTRAR MENSAJE DEL USUARIO
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            mensaje_usuario
        )


    # --------------------------------------------------------
    # 6. EJECUTAR AGENTE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Analizando..."):

            try:

                resultado = responder(
                    mensaje_usuario=mensaje_usuario,
                    nombre_negocio=nombre_puesto,
                    memoria=memoria,
                )


                # ------------------------------------------------
                # 7. EXTRAER RESPUESTA
                # ------------------------------------------------

                respuesta = resultado.get(
                    "respuesta",
                    "No se obtuvo una respuesta."
                )


                # ------------------------------------------------
                # 8. MOSTRAR RESPUESTA
                # ------------------------------------------------

                st.markdown(
                    respuesta
                )


                # ------------------------------------------------
                # 9. GUARDAR RESPUESTA EN MEMORIA
                # ------------------------------------------------

                agregar_mensaje(
                    "assistant",
                    respuesta
                )


                # ------------------------------------------------
                # 10. REGISTRAR TRAZABILIDAD
                # ------------------------------------------------

                registrar_ejecucion(
                    resultado
                )


                # ------------------------------------------------
                # 11. RECARGAR INTERFAZ
                # ------------------------------------------------

                st.rerun()


            except Exception as error:

                st.error(
                    "Ocurrió un error al consultar "
                    f"el agente: {error}"
                )