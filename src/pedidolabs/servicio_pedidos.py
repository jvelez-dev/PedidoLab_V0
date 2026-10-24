from .cliente import Cliente
from .pedido import Pedido
from .precios import calcular_descuento, calcular_beneficio_fidelidad
from .envios import calcular_costo_envio
from .pagos import PayFastAPI, cobrar_con_payfast
from .notificaciones import enviar_email_confirmacion, enviar_email_pago
from .repositorio import RepositorioArchivo
from .facturacion import generar_factura

class ServicioPedidos:

    def __init__(self, inventario, ruta_pedidos="pedidos.jsonl"):
        self.inventario = inventario
        self.ruta_pedidos = ruta_pedidos
        self.payfast = PayFastAPI()
        self.ultima_factura = None
        self.ultimos_puntos = 0

    def _crear_pedido(self, pedido_id, cliente, items):
        pedido = Pedido(
            pedido_id, cliente, cliente.calle, cliente.ciudad,
            cliente.departamento, cliente.codigo_postal,
        )
        if not items:
            raise ValueError("El pedido debe contener al menos un producto")
        for producto, cantidad in items:
            self.inventario.validar_disponibilidad(producto.codigo, cantidad)
            pedido.agregar_item(producto, cantidad)
        return pedido

    def _reservar_inventario(self, pedido):
        for item in pedido.items:
            self.inventario.reservar(item.producto.codigo, item.cantidad)

    def _confirmar(self, pedido, transaccion_id, total):
        pedido.estado = "CONFIRMADO"
        pedido.transaccion_id = transaccion_id
        pedido.total_pagado = total
        repo = RepositorioArchivo(self.ruta_pedidos)
        repo.guardar(pedido)


    def procesar_pedido(
        self, pedido_id, documento, nombre, email, telefono, tipo_cliente,
        calle, ciudad, departamento, codigo_postal, items, numero_tarjeta,
        enviar_confirmacion=True,
    ):
        cliente = Cliente(
            documento, nombre, email, telefono, tipo_cliente,
            calle, ciudad, departamento, codigo_postal,
        )
        pedido = self._crear_pedido(pedido_id, cliente, items)        
        resumen_pedido = self.calcular_resumen(pedido)
        subtotal = resumen_pedido["subtotal"]
        descuento = resumen_pedido["descuento"]
        envio = resumen_pedido["envio"]
        total = resumen_pedido["total"]

        transaccion_id = cobrar_con_payfast(
            self.payfast, numero_tarjeta=numero_tarjeta, monto=total
        )

        self._reservar_inventario(pedido)
        self._confirmar(pedido, transaccion_id, total)
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