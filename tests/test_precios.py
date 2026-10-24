import pytest
from pedidolabs.cliente import Cliente
from pedidolabs.pedido import Pedido
from pedidolabs.producto import Producto
from pedidolabs.precios import (
    calcular_descuento,
    descripcion_descuento,
    calcular_beneficio_fidelidad,
    calcular_total_con_descuento,
)


def cliente(tipo):
    return Cliente("9", "Test", "t@test.com", "300", tipo)


# --- calcular_descuento: umbrales exactos -------------------------------

@pytest.mark.parametrize("tipo, subtotal, esperado", [
    ("NORMAL", 2_000_000, 0.0),
    ("PREMIUM", 499_999, 499_999 * 0.10),
    ("PREMIUM", 500_000, 500_000 * 0.15),
    ("CORPORATIVO", 999_999, 999_999 * 0.12),
    ("CORPORATIVO", 1_000_000, 1_000_000 * 0.20),
    ("VIP", 2_000_000, 0.0),          # tipo desconocido: sin descuento
])
def test_descuento_en_los_umbrales(tipo, subtotal, esperado):
    assert calcular_descuento(cliente(tipo), subtotal) == esperado


# --- descripcion_descuento: todos los tipos y ramas ---------------------

@pytest.mark.parametrize("tipo, subtotal, esperado", [
    ("NORMAL", 2_000_000, "Sin descuento"),
    ("PREMIUM", 499_999, "Cliente PREMIUM: 10%"),
    ("PREMIUM", 500_000, "Cliente PREMIUM: 15%"),
    ("CORPORATIVO", 999_999, "Cliente CORPORATIVO: 12%"),
    ("CORPORATIVO", 1_000_000, "Cliente CORPORATIVO: 20%"),
    ("VIP", 2_000_000, "Sin descuento"),
])
def test_descripcion_por_tipo_y_umbral(tipo, subtotal, esperado):
    assert descripcion_descuento(cliente(tipo), subtotal) == esperado


# --- calcular_beneficio_fidelidad: todos los tipos ----------------------

@pytest.mark.parametrize("tipo, total, esperado", [
    ("NORMAL", 149_999, 2),
    ("NORMAL", 150_000, 3),
    ("PREMIUM", 74_999, 2),
    ("PREMIUM", 75_000, 3),
    ("CORPORATIVO", 59_999, 2),
    ("CORPORATIVO", 60_000, 3),
    ("VIP", 1_000_000, 0),
])
def test_puntos_de_fidelidad_por_tipo(tipo, total, esperado):
    puntos = calcular_beneficio_fidelidad(cliente(tipo), total)
    assert puntos == esperado
    assert isinstance(puntos, int)


# --- calcular_total_con_descuento: no tenía prueba ----------------------

def test_total_con_descuento_usa_subtotal_del_pedido():
    pedido = Pedido("PZ", cliente("PREMIUM"), "Calle 1", "Manizales", "Caldas", "170001")
    pedido.agregar_item(Producto("A", "A", 100_000, 1.0), 5)   # subtotal 500.000
    assert calcular_total_con_descuento(pedido) == 500_000 - 75_000