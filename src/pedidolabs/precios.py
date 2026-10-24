def _porcentaje_descuento(cliente, subtotal):
    if cliente.tipo == "PREMIUM":
        if subtotal >= 500_000:
            return 0.15
        return 0.10
    if cliente.tipo == "CORPORATIVO":
        if subtotal >= 1_000_000:
            return 0.20
        return 0.12
    return 0.0

def calcular_descuento(cliente, subtotal):
    return subtotal * _porcentaje_descuento(cliente, subtotal)

def descripcion_descuento(cliente, subtotal):
    porcentaje = _porcentaje_descuento(cliente, subtotal)
    if porcentaje == 0:
        return "Sin descuento"
    return f"Cliente {cliente.tipo}: {round(porcentaje * 100)}%"

def calcular_beneficio_fidelidad(cliente, total):
    if cliente.tipo == "NORMAL":
        return int(total // 50_000)
    if cliente.tipo == "PREMIUM":
        return int(total // 25_000)
    if cliente.tipo == "CORPORATIVO":
        return int(total // 20_000)
    return 0

def calcular_total_con_descuento(pedido):
    subtotal = pedido.subtotal()
    return subtotal - calcular_descuento(pedido.cliente, subtotal)
