from .cliente import Cliente
from .pedido import Pedido
from .precios import calcular_descuento, calcular_beneficio_fidelidad
from .envios import calcular_costo_envio
from .pagos import PayFastAPI, cobrar_con_payfast
from .notificaciones import enviar_email_confirmacion, enviar_email_pago
from .repositorio import RepositorioArchivo
from .facturacion import generar_factura
from .dto import ProcesarPedidoDTO

class ServicioPedidos:

    def __init__(self, inventario, ruta_pedidos="pedidos.jsonl", cobrar=None):
        self.inventario = inventario
        self.ruta_pedidos = ruta_pedidos
        payfast = PayFastAPI()
        self.cobrar = cobrar or (
            lambda numero_tarjeta, monto: cobrar_con_payfast(payfast, numero_tarjeta, monto)
        )
        self.ultima_factura = None
        self.ultimos_puntos = 0
    
    def crear_cliente_pedido(self, dto: ProcesarPedidoDTO):
        cliente = Cliente(
            dto.documento, dto.nombre, dto.email, dto.telefono, dto.tipo_cliente,
            dto.calle, dto.ciudad, dto.departamento, dto.codigo_postal,
        )
        pedido = Pedido(
            dto.pedido_id, cliente, dto.calle, dto.ciudad, dto.departamento,
            dto.codigo_postal,
        )
        return cliente, pedido

    def _validar_stock(self, items):
        for producto, cantidad in items:
            self.inventario.validar_disponibilidad(producto.codigo, cantidad)

    def _agregar_items(self, pedido, items):
        for producto, cantidad in items:
            pedido.agregar_item(producto, cantidad)

    def procesar_pedido(self, dto: ProcesarPedidoDTO):

        if not dto.items:
            raise ValueError("El pedido debe contener al menos un producto")

        self._validar_stock(dto.items)
        cliente, pedido = self.crear_cliente_pedido(dto);
        self._agregar_items(pedido, dto.items)

        subtotal = pedido.subtotal()

        descuento = calcular_descuento(cliente, subtotal)
        envio = calcular_costo_envio(pedido, modalidad="ESTANDAR")
        total = subtotal - descuento + envio

        transaccion_id = self.cobrar(dto.numero_tarjeta, total)

        for item in pedido.items:
            self.inventario.reservar(item.producto.codigo, item.cantidad)

        pedido.estado = "CONFIRMADO"
        pedido.transaccion_id = transaccion_id
        pedido.total_pagado = total

        repo = RepositorioArchivo(self.ruta_pedidos)
        repo.guardar(pedido)

        self.ultima_factura = generar_factura(pedido, subtotal, descuento, envio)
        self.ultimos_puntos = calcular_beneficio_fidelidad(cliente, total)

        enviar_email_pago(cliente, pedido.id, transaccion_id, total)
        if dto.enviar_confirmacion:
            enviar_email_confirmacion(cliente, pedido.id, total)
        return pedido

    def calcular_resumen(self, pedido):
        subtotal = pedido.subtotal()
        descuento = calcular_descuento(pedido.cliente, subtotal)
        envio = calcular_costo_envio(pedido)
        return {
            "subtotal": subtotal,
            "descuento": descuento,
            "envio": envio,
            "total": subtotal - descuento + envio,
        }
