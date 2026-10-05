from datetime import datetime
from model.cliente import Cliente
from model.personal import Personal
from model.medicamento import Medicamento
from model.receta import Receta
from model.detalle_venta import DetalleVenta


class Venta:
    def __init__(self, cliente: Cliente, vendedor: Personal, fecha: str = None):
        self._cliente = cliente
        self._vendedor = vendedor
        self._fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M")
        self._detalles = []
        self._total = 0.0

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def vendedor(self) -> Personal:
        return self._vendedor

    @property
    def fecha(self) -> str:
        return self._fecha

    @property
    def detalles(self) -> list:
        return self._detalles

    @property
    def total(self) -> float:
        return self._total

    def agregar_detalle(self, medicamento: Medicamento, cantidad: int, receta: Receta = None, valor_dolar: float = 950.0) -> DetalleVenta:

        medicamento.validar_venta(receta)

        if medicamento.stock < cantidad:
            raise ValueError(f"Stock insuficiente para '{medicamento.nombre}'. Disponible: {medicamento.stock}, solicitado: {cantidad}.")

        medicamento.stock -= cantidad

        detalle = DetalleVenta(medicamento, cantidad, receta, valor_dolar)
        self._detalles.append(detalle)
        self.calcular_total(valor_dolar)
        return detalle

    def calcular_total(self, valor_dolar: float = 950.0) -> float:
        self._total = sum(det.calcular_subtotal(valor_dolar) for det in self._detalles)
        return self._total
