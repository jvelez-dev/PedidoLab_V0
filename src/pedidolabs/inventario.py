class Inventario:
    def __init__(self, stock_inicial=None):
        self.stock = dict(stock_inicial or {})

    @staticmethod
    def validarCantidadPositiva(cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")

    def validar_disponibilidad(self, codigo):
        if codigo not in self.stock:
            raise ValueError(f"Producto {codigo} no existe en inventario")

    def verificarStockSuficiente(self, codigo, cantidad):
        self.validar_disponibilidad(codigo)
        if self.stock[codigo] < cantidad:
            raise ValueError(
                f"Stock insuficiente para {codigo}: "
                f"disponible={self.stock[codigo]}, solicitado={cantidad}"
            )

    def reservar(self, codigo, cantidad):
        self.validarCantidadPositiva(cantidad)
        self.verificarStockSuficiente(codigo, cantidad)
        self.stock[codigo] -= cantidad

    def devolver(self, codigo, cantidad):
        self.validarCantidadPositiva(cantidad)
        self.validar_disponibilidad(codigo)
        self.stock[codigo] += cantidad

    def ajustar(self, codigo, cantidad):
        if cantidad < 0:
            raise ValueError("El ajuste no puede ser negativo")
        self.validar_disponibilidad(codigo)
        self.stock[codigo] = cantidad

    def disponible(self, codigo):
        self.validar_disponibilidad(codigo)
        return self.stock[codigo]
