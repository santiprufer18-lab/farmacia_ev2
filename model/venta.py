from datetime import datetime
from model.cliente import Cliente
from model.personal import Personal
from model.medicamento import Medicamento
from model.receta import Receta
from model.detalle_venta import DetalleVenta


class Venta:
    def __init__(self, cliente: Cliente, vendedor: Personal, fecha: str = None, total: float = 0.0, id_venta: int = None):
        self._id_venta = id_venta
        self._cliente = cliente
        self._vendedor = vendedor
        self._fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._detalles = []
        self._total = float(total)

    @property
    def id_venta(self) -> int:
        return self._id_venta

    @id_venta.setter
    def id_venta(self, valor: int):
        self._id_venta = valor

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
        # Validar venta segun reglas de negocio del medicamento
        medicamento.validar_venta(receta)

        # Regla de negocio: Verificar stock disponible
        if medicamento.stock < cantidad:
            raise ValueError(f"Stock insuficiente para '{medicamento.nombre}'. Disponible: {medicamento.stock}, solicitado: {cantidad}.")

        # Descontar stock del objeto medicamento
        medicamento.stock -= cantidad

        detalle = DetalleVenta(medicamento, cantidad, receta, valor_dolar)
        self._detalles.append(detalle)
        self.calcular_total(valor_dolar)
        return detalle

    def agregar_detalle_existente(self, detalle: DetalleVenta):
        """Agrega un detalle previamente cargado desde la base de datos."""
        self._detalles.append(detalle)
        self._total = round(sum(d.subtotal for d in self._detalles), 2)

    def calcular_total(self, valor_dolar: float = 950.0) -> float:
        self._total = round(sum(det.calcular_subtotal(valor_dolar) for det in self._detalles), 2)
        return self._total
