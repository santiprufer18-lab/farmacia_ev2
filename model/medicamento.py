from datetime import datetime, date
from model.excepciones import MedicamentoVencidoException


class Medicamento:
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False):
        self._nombre = nombre
        self.precio_base = precio_base
        self.stock = stock
        self.fecha_vencimiento = fecha_vencimiento
        self._es_importado = es_importado

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        if valor <= 0:
            raise ValueError("El precio base del medicamento debe ser mayor a 0.")
        self._precio_base = float(valor)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int):
        if valor < 0:
            raise ValueError("El stock del medicamento no puede ser negativo.")
        self._stock = int(valor)

    @property
    def fecha_vencimiento(self) -> str:
        return self._fecha_vencimiento

    @fecha_vencimiento.setter
    def fecha_vencimiento(self, fecha_str: str):
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            self._fecha_vencimiento = fecha_str
        except ValueError:
            raise ValueError("La fecha de vencimiento debe tener el formato AAAA-MM-DD.")

    @property
    def es_importado(self) -> bool:
        return self._es_importado

    # Metodos del negocio
    def esta_vencido(self) -> bool:
        fecha_venc = datetime.strptime(self._fecha_vencimiento, "%Y-%m-%d").date()
        return fecha_venc < date.today()

    def get_precio_final(self, valor_dolar: float = 950.0) -> float:
        """Calcula el precio final considerando si es un producto importado y el valor del dolar."""
        if self._es_importado:
            return self._precio_base * valor_dolar
        return self._precio_base

    def validar_venta(self, receta=None) -> bool:
        if self.esta_vencido():
            raise MedicamentoVencidoException(self._nombre, self._fecha_vencimiento)
        return True
