
"""Interfaz principal del asistente inteligente para Picanteo.

Coordina Streamlit, el contexto del negocio y la ejecución
del grafo de LangGraph.
"""

import streamlit as st

from langchain_core.messages import HumanMessage

from config.settings import validar_configuracion
from core.session import (
    invocar_grafo,
    inicializar_thread_id,
    crear_nueva_sesion_grafo,
)
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
# INICIALIZAR ESTADO Y SESIÓN DEL GRAFO
# ============================================================

inicializar_estado()
inicializar_thread_id()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def extraer_texto(mensaje) -> str:
    """Extrae el texto de un mensaje de LangChain."""

    contenido = mensaje.content

    if isinstance(contenido, str):
        return contenido.strip()

    if isinstance(contenido, list):
        partes = []

        for bloque in contenido:
            if isinstance(bloque, str):
                partes.append(bloque)

            elif isinstance(bloque, dict):
                if bloque.get("type") == "text":
                    partes.append(str(bloque.get("text", "")))

        return "\n".join(
            parte for parte in partes if parte
        ).strip()

    return str(contenido)


def extraer_respuesta_final(resultado: dict) -> str:
    """
    Busca la última respuesta del asistente que no sea
    una solicitud de ejecución de herramientas.
    """

    for mensaje in reversed(resultado.get("messages", [])):
        if getattr(mensaje, "type", "") != "ai":
            continue

        # Un mensaje que solicita herramientas todavía no
        # representa la respuesta final para el usuario.
        if getattr(mensaje, "tool_calls", None):
            continue

        texto = extraer_texto(mensaje)

        if texto:
            return texto

    return "No fue posible generar una respuesta final."


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

    st.subheader("🏪 Negocio")
    st.write(
        contexto_negocio.get("nombre_puesto")
        or "Aún no identificado"
    )

    st.subheader("💬 Mensajes")
    st.write(len(st.session_state.mensajes))

    st.subheader("🧵 Sesión LangGraph")
    st.code(st.session_state.thread_id)

    st.subheader("⚙️ Última ejecución")
    st.write(estado.get("ruta", "Sin ejecución"))

    st.subheader("🧭 Motivo")
    st.write(estado.get("motivo") or "Sin información")

    st.subheader("🔧 Tools utilizadas")
    tools = estado.get("tools", [])

    if tools:
        for tool in tools:
            st.write(f"• {tool}")
    else:
        st.write("Ninguna")

    st.divider()

    if st.button("🔄 Nueva conversación"):
        # Reinicia el historial visual y el contexto del negocio.
        reiniciar_estado()

        # Asigna un hilo distinto para no recuperar el anterior.
        crear_nueva_sesion_grafo()

        st.rerun()


# ============================================================
# MOSTRAR HISTORIAL VISUAL
# ============================================================

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])


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

    # 1. Actualizar el contexto del negocio.
    actualizar_contexto_negocio(mensaje_usuario)

    contexto_negocio = obtener_contexto_negocio()
    nombre_puesto = contexto_negocio.get("nombre_puesto", "")

    # 2. Obtener la memoria previa antes de guardar la pregunta.
    # Así no repetimos la pregunta actual dentro del prompt.
    memoria = obtener_memoria()

    # 3. Guardar la pregunta en el historial visual.
    agregar_mensaje("user", mensaje_usuario)

    with st.chat_message("user"):
        st.markdown(mensaje_usuario)

    with st.chat_message("assistant"):
        with st.spinner("Analizando con LangGraph..."):

            try:
                # 4. Enviar únicamente el mensaje nuevo al grafo.
                estado_inicial = {
                    "messages": [
                        HumanMessage(content=mensaje_usuario)
                    ],
                    "nombre_negocio": nombre_puesto,
                    "memoria": memoria,
                }

                # 5. Ejecutar el grafo con el thread_id de la sesión.
                resultado = invocar_grafo(estado_inicial)

                # 6. Extraer la respuesta final del asistente.
                respuesta = extraer_respuesta_final(resultado)

                # 7. Mostrar y guardar la respuesta en la interfaz.
                st.markdown(respuesta)
                agregar_mensaje("assistant", respuesta)

                # 8. Adaptar la salida del grafo al formato que
                # espera el panel lateral existente.
                ruta_grafo = resultado.get("ruta", "agent")

                resultado_ui = {
                    "ruta": (
                        "Chain" if ruta_grafo == "chain"
                        else "Agent"
                    ),
                    "motivo": resultado.get("motivo", ""),
                    "tools": resultado.get(
                        "herramientas_usadas", []
                    ),
                }

                registrar_ejecucion(resultado_ui)

                # 9. Actualizar el panel y el historial.
                st.rerun()

            except Exception as error:
                st.error(
                    "Ocurrió un error al consultar "
                    f"el agente: {error}"
                )
