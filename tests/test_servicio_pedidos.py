import pytest
from pedidolabs.producto import Producto
from pedidolabs.inventario import Inventario
from pedidolabs.servicio_pedidos import ServicioPedidos
from pedidolabs.repositorio import RepositorioArchivo
from pedidolabs.notificaciones import MENSAJES_ENVIADOS, limpiar_bandeja

def crear_servicio(tmp_path):
    inventario = Inventario({"A": 10})
    repositorio = RepositorioArchivo(tmp_path / "pedidos.jsonl")
    return ServicioPedidos(inventario, repositorio), inventario

def args_base(prod):
    return (
        "P1", "1", "Ana", "ana@test.com", "300", "NORMAL",
        "Calle 1", "Manizales", "Caldas", "170001",
        [(prod, 2)], "4111111111111111"
    )

def test_procesar_pedido_confirma_y_cobra(tmp_path):
    limpiar_bandeja()
    servicio, inventario = crear_servicio(tmp_path)
    prod = Producto("A", "Producto", 100_000, 1)
    p = servicio.procesar_pedido(*args_base(prod))
    assert p.estado == "CONFIRMADO"
    assert p.transaccion_id.startswith("PF-")
    assert inventario.disponible("A") == 8

def test_procesar_pedido_persiste(tmp_path):
    limpiar_bandeja()
    servicio, _ = crear_servicio(tmp_path)
    prod = Producto("A", "Producto", 100_000, 1)
    servicio.procesar_pedido(*args_base(prod))
    datos = RepositorioArchivo(tmp_path / "pedidos.jsonl").listar()
    assert len(datos) == 1 and datos[0]["id"] == "P1"

def test_procesar_pedido_genera_factura_y_notifica(tmp_path):
    limpiar_bandeja()
    servicio, _ = crear_servicio(tmp_path)
    prod = Producto("A", "Producto", 100_000, 1)
    servicio.procesar_pedido(*args_base(prod))
    assert "FACTURA P1" in servicio.ultima_factura
    assert len(MENSAJES_ENVIADOS) == 2

def test_pedido_sin_items_falla(tmp_path):
    servicio, _ = crear_servicio(tmp_path)
    with pytest.raises(ValueError, match="al menos un producto"):
        servicio.procesar_pedido(
            "P1", "1", "Ana", "ana@test.com", "300", "NORMAL",
            "Calle 1", "Manizales", "Caldas", "170001",
            [], "4111111111111111"
        )
