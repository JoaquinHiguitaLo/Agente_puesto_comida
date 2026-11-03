
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
