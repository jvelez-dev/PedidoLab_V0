from dataclasses import dataclass


@dataclass(frozen=True)
class PoliticaCliente:
    porcentaje_base: float
    porcentaje_alto: float
    umbral_alto: float

    def porcentaje_descuento_cliente(self, subtotal):
        if subtotal >= self.umbral_alto:
            return self.porcentaje_alto
        return self.porcentaje_base


POLITICAS = {
    "NORMAL": PoliticaCliente(porcentaje_base=0.0, porcentaje_alto=0.0, umbral_alto=0),
    "PREMIUM": PoliticaCliente(porcentaje_base=0.10, porcentaje_alto=0.15, umbral_alto=500_000),
    "CORPORATIVO": PoliticaCliente(porcentaje_base=0.12, porcentaje_alto=0.20, umbral_alto=1_000_000),
    "VIP": PoliticaCliente(porcentaje_base=0.0, porcentaje_alto=0.0, umbral_alto=0),
}


def _porcentaje_descuento(cliente, subtotal):
    politica = POLITICAS.get(cliente.tipo)
    if politica is None:
        return 0.0
    return politica.porcentaje_descuento_cliente(subtotal)

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