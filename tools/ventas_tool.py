"""Herramienta para consultar las ventas del puesto de comida."""

import json
from pathlib import Path


def consultar_ventas() -> dict:
    """Consulta todas las ventas registradas en ventas.json."""

    ruta_archivo = Path(__file__).resolve().parent.parent / "data" / "ventas.json"

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            ventas = json.load(archivo)

        return {
            "ventas": ventas,
            "cantidad": len(ventas),
        }

    except FileNotFoundError:
        return {
            "error": "No se encontró el archivo ventas.json."
        }

    except json.JSONDecodeError:
        return {
            "error": "El archivo ventas.json no contiene un JSON válido."
        }