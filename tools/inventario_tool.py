"""Tool para consultar el inventario del puesto de comida."""

import json
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "inventario.json"


@tool
def consultar_inventario(consulta: str = "todos") -> dict:
    """Consulta productos del inventario por nombre o estado del stock."""

    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        inventario = json.load(archivo)

    criterio = consulta.lower().strip()

    if criterio in {"todos", "todo", "*"}:
        resultados = inventario

    elif criterio in {"bajo", "stock bajo", "agotados"}:
        resultados = [
            producto
            for producto in inventario
            if float(producto["Cantidad stock"]) <= float(producto["Stock minimo"])
        ]

    else:
        resultados = [
            producto
            for producto in inventario
            if criterio in producto["Producto"].lower()
        ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }