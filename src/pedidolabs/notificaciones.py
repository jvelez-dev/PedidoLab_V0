MENSAJES_ENVIADOS = []

def _registrar_envio(destino, asunto, cuerpo):
    MENSAJES_ENVIADOS.append(
        {"canal": "EMAIL", "destino": destino, "asunto": asunto, "cuerpo": cuerpo}
    )

def enviar_email_confirmacion(cliente, pedido_id, total):
    asunto = f"Confirmación pedido {pedido_id}"
    cuerpo = (
        f"Hola {cliente.nombre}, su pedido {pedido_id} fue confirmado. "
        f"Total pagado: ${total:,.0f}."
    )

    _registrar_envio(cliente.email, asunto, cuerpo)

    return cuerpo

def enviar_email_pago(cliente, pedido_id, transaccion_id, total):
    asunto = f"Pago recibido {pedido_id}"
    cuerpo = (
        f"Hola {cliente.nombre}, recibimos el pago del pedido {pedido_id}. "
        f"Transacción {transaccion_id}. Total: ${total:,.0f}."
    )

    _registrar_envio(cliente.email, asunto, cuerpo)

    return cuerpo

def enviar_email_cancelacion(cliente, pedido_id):
    asunto = f"Pedido cancelado {pedido_id}"
    cuerpo = f"Hola {cliente.nombre}, el pedido {pedido_id} fue cancelado."

    _registrar_envio(cliente.email, asunto, cuerpo)

    return cuerpo

def limpiar_bandeja():
    MENSAJES_ENVIADOS.clear()
