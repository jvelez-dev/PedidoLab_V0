from pedidolabs.pedido import Pedido
from pedidolabs.repositorio import RepositorioArchivo

def test_guardar_y_listar(tmp_path, cliente_normal, producto_a):
    p = Pedido("P1", cliente_normal, "x", "Manizales", "Caldas", "170001")
    p.agregar_item(producto_a, 1)
    p.estado = "CONFIRMADO"
    p.total_pagado = 108_000
    p.transaccion_id = "T1"
    repo = RepositorioArchivo(tmp_path / "pedidos.jsonl")
    repo.guardar(p)
    datos = repo.listar()
    assert datos[0]["id"] == "P1"
    assert datos[0]["total_pagado"] == 108_000

def test_listar_vacio(tmp_path):
    assert RepositorioArchivo(tmp_path / "x.jsonl").listar() == []