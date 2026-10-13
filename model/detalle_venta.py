from model.medicamento import Medicamento
from model.receta import Receta


class DetalleVenta:
    def __init__(self, medicamento: Medicamento, cantidad: int, receta: Receta = None, valor_dolar: float = 950.0, precio_unitario: float = None, id_detalle: int = None, id_venta: int = None):
        self._id_detalle = id_detalle
        self._id_venta = id_venta
        self._medicamento = medicamento
        self.cantidad = cantidad
        self._receta = receta
        if precio_unitario is not None:
            self._precio_unitario = float(precio_unitario)
        else:
            self._precio_unitario = float(medicamento.get_precio_final(valor_dolar))
        self._subtotal = round(self._precio_unitario * self._cantidad, 2)

    @property
    def id_detalle(self) -> int:
        return self._id_detalle

    @id_detalle.setter
    def id_detalle(self, valor: int):
        self._id_detalle = valor

    @property
    def id_venta(self) -> int:
        return self._id_venta

    @id_venta.setter
    def id_venta(self, valor: int):
        self._id_venta = valor

    @property
    def medicamento(self) -> Medicamento:
        return self._medicamento

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int):
        try:
            val_num = int(valor)
        except (ValueError, TypeError):
            raise ValueError("La cantidad debe ser un numero entero.")
        if val_num <= 0:
            raise ValueError("La cantidad de medicamentos en el detalle debe ser al menos 1.")
        self._cantidad = val_num

    @property
    def receta(self) -> Receta:
        return self._receta

    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @property
    def subtotal(self) -> float:
        return self._subtotal

    def calcular_subtotal(self, valor_dolar: float = 950.0) -> float:
        self._precio_unitario = self._medicamento.get_precio_final(valor_dolar)
        self._subtotal = round(self._precio_unitario * self._cantidad, 2)
        return self._subtotal
