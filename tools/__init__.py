
"""
Exportación centralizada de las herramientas del negocio.

Este módulo reúne las herramientas existentes para que el agente
y el ToolNode de LangGraph puedan utilizarlas desde un solo lugar.
"""

from tools.fecha_tool import obtener_fecha
from tools.ventas_tool import consultar_ventas
from tools.inventario_tool import consultar_inventario
from tools.proveedores_tool import consultar_proveedores
from tools.compras_tool import consultar_compras
from tools.productos_tool import consultar_productos


# Lista única de herramientas disponibles para el agente.
TOOLS_NEGOCIO = [
    obtener_fecha,
    consultar_ventas,
    consultar_inventario,
    consultar_proveedores,
    consultar_compras,
    consultar_productos,
]
