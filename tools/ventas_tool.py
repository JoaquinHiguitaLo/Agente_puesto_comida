"""Tool para consultar las ventas del puesto de comida."""

import json
from pathlib import Path

from langchain.tools import tool


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "ventas.json"


"""Le comunica a LangChain puede ser utilizada como una herramienta por un Agent"""
@tool
def consultar_ventas() -> dict:
    """Consulta todas las ventas registradas en ventas.json."""

    try:
        with DATA_FILE.open("r", encoding="utf-8") as archivo:
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