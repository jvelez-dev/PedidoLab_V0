from .cliente import Cliente
from .pedido import Pedido
from .precios import calcular_descuento, calcular_beneficio_fidelidad
from .envios import calcular_costo_envio
from .pagos import PayFastAPI, cobrar_con_payfast
from .notificaciones import enviar_email_confirmacion, enviar_email_pago
from .facturacion import generar_factura

class ServicioPedidos:

    def __init__(self, inventario, repositorio):
        self.inventario = inventario
        self.repositorio = repositorio
        self.payfast = PayFastAPI()
        self.ultima_factura = None
        self.ultimos_puntos = 0

    def procesar_pedido(
        self, pedido_id, documento, nombre, email, telefono, tipo_cliente,
        calle, ciudad, departamento, codigo_postal, items, numero_tarjeta,
        enviar_confirmacion=True,
    ):
        cliente = Cliente(
            documento, nombre, email, telefono, tipo_cliente,
            calle, ciudad, departamento, codigo_postal,
        )
        pedido = Pedido(
            pedido_id, cliente, calle, ciudad, departamento, codigo_postal
        )
        if not items:
            raise ValueError("El pedido debe contener al menos un producto")

        for producto, cantidad in items:
            self.inventario.validar_disponibilidad(producto.codigo, cantidad)
            pedido.agregar_item(producto, cantidad)

        subtotal = 0.0
        for item in pedido.items:
            subtotal += item.producto.precio * item.cantidad

        descuento = calcular_descuento(cliente, subtotal)
        envio = calcular_costo_envio(pedido, modalidad="ESTANDAR")
        total = subtotal - descuento + envio

        transaccion_id = cobrar_con_payfast(
            self.payfast, numero_tarjeta=numero_tarjeta, monto=total
        )

        for item in pedido.items:
            self.inventario.reservar(item.producto.codigo, item.cantidad)

        pedido.estado = "CONFIRMADO"
        pedido.transaccion_id = transaccion_id
        pedido.total_pagado = total

        self.repositorio.guardar(pedido)

        self.ultima_factura = generar_factura(pedido, subtotal, descuento, envio)
        self.ultimos_puntos = calcular_beneficio_fidelidad(cliente, total)

        enviar_email_pago(cliente, pedido.id, transaccion_id, total)
        if enviar_confirmacion:
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
