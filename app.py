
"""Interfaz principal del asistente inteligente para Picanteo.

Coordina Streamlit, el contexto del negocio y la ejecución
del grafo de LangGraph.
"""

import streamlit as st

from langchain_core.messages import HumanMessage

from config.settings import validar_configuracion
from core.observability import (
    iniciar_medicion,
    calcular_duracion,
    ObservabilidadCallback,
)
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


def mostrar_estado_ejecucion(contenedor):
    """
    Actualiza los indicadores de la última ejecución.
    """

    estado = obtener_estado_agente()

    with contenedor.container():
        st.subheader("⚙️ Última ejecución")
        st.write(estado.get("ruta", "Sin ejecución"))

        st.subheader("🧭 Motivo")
        st.write(
            estado.get("motivo") or "Sin información"
        )

        st.subheader("🔧 Tools utilizadas")
        herramientas = estado.get("tools", [])

        if herramientas:
            for herramienta in herramientas:
                st.write(f"• {herramienta}")
        else:
            st.write("Ninguna")

        st.subheader("⏱️ Tiempo de respuesta")

        duracion = estado.get("duracion_segundos")

        if duracion is not None:
            st.metric(
                "Duración del grafo",
                f"{duracion:.3f} s"
            )
        else:
            st.write("Sin medición disponible")

        st.subheader("📊 Métricas de Gemini")

        metricas = estado.get("metricas") or {}

        if metricas:
            st.metric(
                "Llamadas completadas",
                metricas.get("llamadas_completadas", 0)
            )

            tokens_entrada = metricas.get("tokens_entrada")
            tokens_salida = metricas.get("tokens_salida")
            tokens_totales = metricas.get("tokens_totales")

            st.write(
                "Tokens de entrada:",
                tokens_entrada if tokens_entrada is not None
                else "No disponibles"
            )

            st.write(
                "Tokens de salida:",
                tokens_salida if tokens_salida is not None
                else "No disponibles"
            )

            st.metric(
                "Tokens totales",
                tokens_totales if tokens_totales is not None
                else "No disponibles"
            )


            errores = metricas.get("errores", [])
            st.write("Errores del modelo:", len(errores))

        else:
            st.write("Sin métricas disponibles")

        # Mostrar errores generales independientemente
        # de que existan métricas de Gemini.
        error_general = estado.get("error_general")

        if error_general:
            st.subheader("⚠️ Estado de ejecución")
            st.error(
                "Se produjo un error durante la ejecución."
            )



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

    contenedor_estado = st.empty()
    mostrar_estado_ejecucion(contenedor_estado)

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

            callback = ObservabilidadCallback()
            inicio = iniciar_medicion()

            try:
                # 4. Enviar únicamente el mensaje nuevo al grafo.
                estado_inicial = {
                    "messages": [
                        HumanMessage(content=mensaje_usuario)
                    ],
                    "nombre_negocio": nombre_puesto,
                    "memoria": memoria,
                }


                # 5. Ejecutar el grafo con observabilidad.

                resultado = invocar_grafo(
                    estado_inicial,
                    callback=callback,
                )
                print(
                    "TIPOS DE MENSAJES:",
                    [
                        {
                            "tipo": getattr(mensaje, "type", None),
                            "tiene_tools": bool(
                                getattr(mensaje, "tool_calls", None)
                            ),
                        }
                        for mensaje in resultado.get("messages", [])
                    ],
                    flush=True,
                )

                duracion = calcular_duracion(inicio)

                metricas = callback.obtener_metricas()


                # 6. Extraer la respuesta final del asistente.
                respuesta = extraer_respuesta_final(resultado)

                # 7. Mostrar y guardar la respuesta en la interfaz.
                st.markdown(respuesta)
                agregar_mensaje("assistant", respuesta)

                # 8. Adaptar la salida del grafo al formato que
                # espera el panel lateral existente.
                ruta_grafo = resultado.get("ruta", "agent")


                resultado_ui = {
                    "ruta": {
                        "chain": "Chain",
                        "agent": "Agent",
                        "rag": "RAG",
                    }.get(ruta_grafo, "Desconocida"),
                    "motivo": resultado.get("motivo", ""),
                    "tools": resultado.get(
                        "herramientas_usadas", []
                    ),
                    "duracion_segundos": duracion,
                    "metricas": metricas,
                }


                registrar_ejecucion(resultado_ui)

                mostrar_estado_ejecucion(contenedor_estado)



            except Exception as error:

                # Registrar duración incluso si falla la ejecución.
                duracion_error = calcular_duracion(inicio)

                # Recuperar las métricas disponibles hasta el fallo.
                metricas_error = callback.obtener_metricas()

                # Guardar información del fallo.
                resultado_error = {
                    "ruta": "Error",
                    "motivo": "La ejecución no finalizó correctamente.",
                    "tools": [],
                    "duracion_segundos": duracion_error,
                    "metricas": metricas_error,
                    "error_general": str(error),
                }

                registrar_ejecucion(resultado_error)

                # Actualizar los indicadores del panel lateral.
                mostrar_estado_ejecucion(contenedor_estado)

                st.error(
                    "Ocurrió un error al consultar el agente. "
                    "Revisa el registro de ejecución."
                )
