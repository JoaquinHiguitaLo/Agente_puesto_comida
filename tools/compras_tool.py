"""Tool para consultar las compras del puesto de comida."""

import json
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "compras.json"


@tool
def consultar_compras(consulta: str = "todas") -> dict:
    """Consulta las compras registradas por fecha, producto o proveedor."""

    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        compras = json.load(archivo)

    criterio = consulta.lower().strip()

    if criterio in {"todas", "todo", "*"}:
        resultados = compras

    else:
        resultados = [
            compra
            for compra in compras
            if (
                criterio in str(compra["fecha"]).lower()
                or criterio in str(compra["id_producto"]).lower()
                or criterio in str(compra["id_proveedor"]).lower()
            )
        ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }