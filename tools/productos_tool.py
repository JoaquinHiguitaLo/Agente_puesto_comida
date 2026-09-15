"""Tool para consultar información de los productos del negocio."""

import json
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "productos.json"


@tool
def consultar_productos(consulta: str) -> dict:
    """Consulta productos por nombre, categoría o palabra clave."""

    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        productos = json.load(archivo)

    criterio = consulta.lower().strip()

    resultados = [
        producto
        for producto in productos
        if criterio in producto["producto"].lower()
        or criterio in producto["categoria"].lower()
        or criterio in producto["unidad"].lower()
    ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }