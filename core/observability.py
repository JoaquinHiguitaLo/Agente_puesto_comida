
from time import perf_counter


def iniciar_medicion():
    """
    Registra el instante en que comienza una ejecución.
    """
    return perf_counter()


def calcular_duracion(inicio):
    """
    Calcula los segundos transcurridos desde el inicio.
    """
    duracion = perf_counter() - inicio
    return round(duracion, 3)


def extraer_metricas_tokens(mensajes):
    """
    Extrae los tokens reportados en los mensajes del modelo.

    No estima tokens cuando los metadatos no están disponibles.
    """

    tokens_entrada = 0
    tokens_salida = 0
    mensajes_con_metricas = 0

    for mensaje in mensajes:
        if getattr(mensaje, "type", None) != "ai":
            continue

        uso = getattr(mensaje, "usage_metadata", None)

        if not isinstance(uso, dict):
            continue

        entrada = uso.get("input_tokens")
        salida = uso.get("output_tokens")

        if entrada is None or salida is None:
            continue

        tokens_entrada += entrada
        tokens_salida += salida
        mensajes_con_metricas += 1

    if mensajes_con_metricas == 0:
        return None

    return {
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida,
        "tokens_totales": tokens_entrada + tokens_salida,
        "mensajes_con_metricas": mensajes_con_metricas,
    }


from langchain_core.callbacks import BaseCallbackHandler


class ObservabilidadCallback(BaseCallbackHandler):
    """Registra métricas de las llamadas al modelo."""

    def __init__(self):
        self.llamadas_completadas = 0
        self.errores = []
        self.tokens_entrada = 0
        self.tokens_salida = 0
        self.respuestas_con_tokens = 0

    def on_llm_end(self, response, **kwargs):
        """Se ejecuta al finalizar una llamada al modelo."""

        self.llamadas_completadas += 1

        for generacion in response.generations:
            for elemento in generacion:
                mensaje = getattr(elemento, "message", None)

                if mensaje is None:
                    continue

                uso = getattr(
                    mensaje,
                    "usage_metadata",
                    None,
                )

                if not isinstance(uso, dict):
                    continue

                entrada = uso.get("input_tokens")
                salida = uso.get("output_tokens")

                if entrada is None or salida is None:
                    continue

                self.tokens_entrada += entrada
                self.tokens_salida += salida
                self.respuestas_con_tokens += 1

    def on_llm_error(self, error, **kwargs):
        """Registra errores de invocación del modelo."""

        self.errores.append(str(error))

    def obtener_metricas(self):
        """Devuelve un resumen de métricas registradas."""

        hay_tokens = self.respuestas_con_tokens > 0

        return {
            "llamadas_completadas": self.llamadas_completadas,
            "tokens_entrada": (
                self.tokens_entrada if hay_tokens else None
            ),
            "tokens_salida": (
                self.tokens_salida if hay_tokens else None
            ),
            "tokens_totales": (
                self.tokens_entrada + self.tokens_salida
                if hay_tokens else None
            ),
            "respuestas_con_tokens": self.respuestas_con_tokens,
            "errores": self.errores.copy(),
        }
