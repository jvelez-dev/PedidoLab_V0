"""Pruebas de caracterización: fijan el comportamiento observable actual
de ServicioPedidos ANTES de refactorizar (red de seguridad)."""
import json
import pytest
from pedidolabs.producto import Producto
from pedidolabs.inventario import Inventario
from pedidolabs.servicio_pedidos import ServicioPedidos
from pedidolabs.notificaciones import MENSAJES_ENVIADOS, limpiar_bandeja

PROD_A = Producto("A", "A", 100_000, 1.0)
PROD_B = Producto("B", "B", 250_000, 2.5)


def procesar(tmp_path, tarjeta="4111111111111111", enviar_confirmacion=True):
    limpiar_bandeja()
    inventario = Inventario({"A": 10, "B": 5})
    servicio = ServicioPedidos(inventario, tmp_path / "pedidos.jsonl")
    pedido = servicio.procesar_pedido(
        "P9", "9", "Paula", "paula@test.com", "300", "PREMIUM",
        "Calle 1", "Pereira", "Risaralda", "660001",
        [(PROD_A, 2), (PROD_B, 1)], tarjeta,
        enviar_confirmacion=enviar_confirmacion,
    )
    return servicio, inventario, pedido


def test_total_factura_y_puntos(tmp_path):
    servicio, _, pedido = procesar(tmp_path)
    assert pedido.total_pagado == 427_000
    assert servicio.ultima_factura == (
        "FACTURA P9\nCliente: Paula\nDocumento: 9\n"
        "Subtotal: $450,000\nDescuento: $45,000\n"
        "Envío: $22,000\nTOTAL: $427,000"
    )
    assert servicio.ultimos_puntos == 17


def test_mensajes_en_orden(tmp_path):
    procesar(tmp_path)
    assert [m["asunto"] for m in MENSAJES_ENVIADOS] == [
        "Pago recibido P9", "Confirmación pedido P9"
    ]
    assert MENSAJES_ENVIADOS[0]["cuerpo"] == (
        "Hola Paula, recibimos el pago del pedido P9. "
        "Transacción PF-00001. Total: $427,000."
    )


def test_sin_confirmacion_solo_envia_pago(tmp_path):
    procesar(tmp_path, enviar_confirmacion=False)
    assert len(MENSAJES_ENVIADOS) == 1


def test_registro_persistido(tmp_path):
    procesar(tmp_path)
    linea = (tmp_path / "pedidos.jsonl").read_text(encoding="utf-8").strip()
    assert json.loads(linea) == {
        "id": "P9", "cliente": "9", "estado": "CONFIRMADO",
        "total_pagado": 427000.0, "transaccion_id": "PF-00001",
        "ciudad": "Pereira",
        "items": [
            {"codigo": "A", "cantidad": 2, "precio": 100000},
            {"codigo": "B", "cantidad": 1, "precio": 250000},
        ],
    }


def test_pago_rechazado_no_reserva_ni_persiste_ni_notifica(tmp_path):
    limpiar_bandeja()
    inventario = Inventario({"A": 10, "B": 5})
    servicio = ServicioPedidos(inventario, tmp_path / "pedidos.jsonl")
    with pytest.raises(ValueError, match="Tarjeta inválida"):
        servicio.procesar_pedido(
            "P9", "9", "Paula", "paula@test.com", "300", "PREMIUM",
            "Calle 1", "Pereira", "Risaralda", "660001",
            [(PROD_A, 2)], "123",
        )
    assert inventario.disponible("A") == 10
    assert not (tmp_path / "pedidos.jsonl").exists()
    assert MENSAJES_ENVIADOS == []


def test_stock_insuficiente_falla_antes_de_cobrar(tmp_path):
    limpiar_bandeja()
    inventario = Inventario({"A": 1})
    servicio = ServicioPedidos(inventario, tmp_path / "pedidos.jsonl")
    with pytest.raises(ValueError, match="Stock insuficiente"):
        servicio.procesar_pedido(
            "P9", "9", "Paula", "paula@test.com", "300", "PREMIUM",
            "Calle 1", "Pereira", "Risaralda", "660001",
            [(PROD_A, 2)], "4111111111111111",
        )
    assert MENSAJES_ENVIADOS == []


def test_calcular_resumen(tmp_path):
    servicio, _, pedido = procesar(tmp_path)
    assert servicio.calcular_resumen(pedido) == {
        "subtotal": 450_000, "descuento": 45_000,
        "envio": 22_000, "total": 427_000,
    }
