from pathlib import Path
from src.pedidolabs.producto import Producto
from src.pedidolabs.inventario import Inventario
from src.pedidolabs.servicio_pedidos import ServicioPedidos
from src.pedidolabs.repositorio import RepositorioArchivo
from src.pedidolabs.notificaciones import MENSAJES_ENVIADOS, limpiar_bandeja

def main():
    limpiar_bandeja()
    teclado = Producto("P001", "Teclado", 120_000, 0.8)
    mouse = Producto("P002", "Mouse", 80_000, 0.3)
    inventario = Inventario({"P001": 10, "P002": 20})

    ruta = Path("demo_pedidos.jsonl")
    if ruta.exists():
        ruta.unlink()

    servicio = ServicioPedidos(inventario, RepositorioArchivo(ruta))
    pedido = servicio.procesar_pedido(
        "PED-001", "123", "Ana", "ana@example.com", "3000000000",
        "PREMIUM", "Cra 23 #45-67", "Manizales", "Caldas", "170001",
        [(teclado, 2), (mouse, 1)], "4111111111111111"
    )

    print("Pedido:", pedido.id, pedido.estado)
    print("Total:", pedido.total_pagado)
    print(servicio.ultima_factura)
    print("Mensajes enviados:", len(MENSAJES_ENVIADOS))

if __name__ == "__main__":
    main()
