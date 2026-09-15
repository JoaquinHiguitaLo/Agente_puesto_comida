"""Tool para consultar información de los proveedores del negocio."""

import json
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "proveedores.json"


@tool
def consultar_proveedores(consulta: str) -> dict:
    """Consulta proveedores por nombre, contacto o identificador."""

    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        proveedores = json.load(archivo)

    criterio = consulta.lower().strip()

    resultados = []

    for proveedor in proveedores:

        # Si la consulta es exactamente un ID, buscar únicamente por ID.
        if criterio.isdigit():
            if criterio == str(proveedor["id_proveedor"]):
                resultados.append(proveedor)

        # Si no es un ID, buscar por nombre o contacto.
        else:
            if (
                criterio in proveedor["nombre"].lower()
                or criterio in proveedor["contacto"].lower()
            ):
                resultados.append(proveedor)

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }