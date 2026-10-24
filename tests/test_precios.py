from pedidolabs.precios import calcular_descuento, descripcion_descuento, calcular_beneficio_fidelidad

def test_normal_no_recibe_descuento(cliente_normal):
    assert calcular_descuento(cliente_normal, 400_000) == 0

def test_premium_recibe_10_por_ciento(cliente_premium):
    assert calcular_descuento(cliente_premium, 300_000) == 30_000

def test_premium_alto_recibe_15_por_ciento(cliente_premium):
    assert calcular_descuento(cliente_premium, 500_000) == 75_000

def test_corporativo_recibe_12_por_ciento(cliente_corporativo):
    assert calcular_descuento(cliente_corporativo, 500_000) == 60_000

def test_corporativo_alto_recibe_20_por_ciento(cliente_corporativo):
    assert calcular_descuento(cliente_corporativo, 1_000_000) == 200_000

def test_descripcion_y_fidelidad(cliente_premium):
    assert descripcion_descuento(cliente_premium, 100_000) == "Cliente PREMIUM: 10%"
    assert calcular_beneficio_fidelidad(cliente_premium, 250_000) == 10