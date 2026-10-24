from enum import Enum


class ModalidadEnvio(str, Enum):
    ESTANDAR = "ESTANDAR"


def calcular_peso(items):
    return sum(item.producto.peso * item.cantidad for item in items)


def calcular_base_domicilio(pedido):
    ciudad = pedido.ciudad.upper()
    departamento = pedido.departamento.upper()

    if departamento == "CALDAS":
        if ciudad == "MANIZALES":
            base = 8_000.0
        else:
            base = 12_000.0
    else:
        base = 18_000.0
    return base

def calcular_subtotal(pedido):
    subtotal = 0.0
    for item in pedido.items:
        subtotal += item.producto.precio * item.cantidad
    return subtotal


def calcular_costo_envio(pedido, modalidad=ModalidadEnvio.ESTANDAR):
    if modalidad not in ModalidadEnvio and modalidad != ModalidadEnvio.ESTANDAR.value:
        raise ValueError("Modalidad de envío no soportada")

    subtotal = calcular_subtotal(pedido)
    if subtotal >= 700_000 and pedido.cliente.tipo in ("PREMIUM", "CORPORATIVO"):
        return 0.0

    peso = calcular_peso(pedido.items)
    base = calcular_base_domicilio(pedido)

    if peso > 10:
        base += 15_000.0
    elif peso > 5:
        base += 8_000.0
    elif peso > 2:
        base += 4_000.0

    return base
