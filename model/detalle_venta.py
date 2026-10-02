from model.medicamento import Medicamento
from model.receta import Receta


class DetalleVenta:
    """
    Representa una línea de detalle dentro de una venta (Composición de Venta, Asociación con Medicamento y Receta).
    """
    def __init__(self, medicamento: Medicamento, cantidad: int, receta: Receta = None, valor_dolar: float = 950.0):
        self._medicamento = medicamento
        self.cantidad = cantidad      # Usa el setter con validación
        self._receta = receta
        self._subtotal = 0.0
        self.calcular_subtotal(valor_dolar)

    @property
    def medicamento(self) -> Medicamento:
        return self._medicamento

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        if valor <= 0:
            raise ValueError("La cantidad de medicamentos en el detalle debe ser al menos 1.")
        self._cantidad = int(valor)

    @property
    def receta(self) -> Receta:
        return self._receta

    @property
    def subtotal(self) -> float:
        return self._subtotal

    def calcular_subtotal(self, valor_dolar: float = 950.0) -> float:
        precio_unitario = self._medicamento.get_precio_final(valor_dolar)
        self._subtotal = precio_unitario * self._cantidad
        return self._subtotal
