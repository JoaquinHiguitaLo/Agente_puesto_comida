
"""Tool para consultar el inventario del puesto de comida."""

import json
import re
import unicodedata
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "inventario.json"


def normalizar_texto(texto: str) -> str:
    """Normaliza acentos, mayúsculas y espacios."""

    texto = unicodedata.normalize("NFKD", texto.lower())

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return re.sub(r"\s+", " ", texto).strip()


@tool
def consultar_inventario(consulta: str = "todos") -> dict:
    """Consulta productos por nombre o estado del stock."""

    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        inventario = json.load(archivo)

    criterio = normalizar_texto(consulta)

    if criterio in {"todos", "todo", "*"}:
        resultados = inventario

    elif (
        criterio in {
            "bajo",
            "stock bajo",
            "agotados",
            "por agotarse",
            "proximos a agotarse",
            "productos proximos a agotarse",
            "existencias bajas",
            "inventario bajo",
        }
        or "stock bajo" in criterio
        or "proximos a agotarse" in criterio
        or "por agotarse" in criterio
    ):
        resultados = [
            producto
            for producto in inventario
            if float(producto["Cantidad stock"])
            <= float(producto["Stock minimo"])
        ]

    else:
        resultados = [
            producto
            for producto in inventario
            if criterio in normalizar_texto(producto["Producto"])
        ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }
