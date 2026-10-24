from dataclasses import dataclass

@dataclass
class ProcesarPedidoDTO:
    pedido_id: str
    documento: str
    nombre: str
    email: str
    telefono: str
    tipo_cliente: str
    calle: str
    ciudad: str
    departamento: str
    codigo_postal: str
    items: list
    numero_tarjeta: str
    enviar_confirmacion: bool = True
