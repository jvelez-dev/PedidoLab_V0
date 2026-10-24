import json
from pathlib import Path

class RepositorioArchivo:
    def __init__(self, ruta="pedidos.jsonl"):
        self.ruta = Path(ruta)

    def guardar(self, pedido):
        registro = {
            "id": pedido.id,
            "cliente": pedido.cliente.documento,
            "estado": pedido.estado,
            "total_pagado": pedido.total_pagado,
            "transaccion_id": pedido.transaccion_id,
            "ciudad": pedido.ciudad,
            "items": [
                {
                    "codigo": item.producto.codigo,
                    "cantidad": item.cantidad,
                    "precio": item.producto.precio,
                }
                for item in pedido.items
            ],
        }
        with self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

    def listar(self):
        if not self.ruta.exists():
            return []
        registros = []
        with self.ruta.open("r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea:
                    registros.append(json.loads(linea))
        return registros
