from datetime import datetime, date
from model.excepciones import MedicamentoVencidoException


class Medicamento:
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False, id_medicamento: int = None):
        self._id_medicamento = id_medicamento
        self.nombre = nombre
        self.precio_base = precio_base
        self.stock = stock
        self.fecha_vencimiento = fecha_vencimiento
        self._es_importado = bool(es_importado)

    @property
    def id_medicamento(self) -> int:
        return self._id_medicamento

    @id_medicamento.setter
    def id_medicamento(self, valor: int):
        self._id_medicamento = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre del medicamento no puede estar vacio.")
        self._nombre = str(valor).strip()

    @property
    def precio_base(self) -> float:
        return self._precio_base

    @precio_base.setter
    def precio_base(self, valor: float):
        try:
            val_num = float(valor)
        except (ValueError, TypeError):
            raise ValueError("El precio base debe ser un numero valido.")
        if val_num <= 0:
            raise ValueError("El precio base del medicamento debe ser mayor a 0.")
        self._precio_base = val_num

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int):
        try:
            val_num = int(valor)
        except (ValueError, TypeError):
            raise ValueError("El stock debe ser un numero entero.")
        if val_num < 0:
            raise ValueError("El stock del medicamento no puede ser negativo.")
        self._stock = val_num

    @property
    def fecha_vencimiento(self) -> str:
        return self._fecha_vencimiento

    @fecha_vencimiento.setter
    def fecha_vencimiento(self, fecha_str: str):
        try:
            datetime.strptime(str(fecha_str).strip(), "%Y-%m-%d")
            self._fecha_vencimiento = str(fecha_str).strip()
        except ValueError:
            raise ValueError("La fecha de vencimiento debe tener el formato AAAA-MM-DD.")

    @property
    def es_importado(self) -> bool:
        return self._es_importado

    @es_importado.setter
    def es_importado(self, valor: bool):
        self._es_importado = bool(valor)

    @property
    def tipo_medicamento(self) -> str:
        return "GENERICO"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente el tipo de receta exigida por el medicamento."""
        return "NINGUNA"

    @property
    def requiere_retencion(self) -> bool:
        """Indica polimorficamente si el medicamento requiere retencion de receta (por defecto False)."""
        return False

    def esta_vencido(self) -> bool:
        fecha_venc = datetime.strptime(self._fecha_vencimiento, "%Y-%m-%d").date()
        return fecha_venc < date.today()

    def get_precio_final(self, valor_dolar: float = 950.0) -> float:
        """Calcula el precio final considerando si es importado y el valor del dolar."""
        if self._es_importado:
            return round(self._precio_base * valor_dolar, 2)
        return round(self._precio_base, 2)

    def validar_venta(self, receta=None) -> bool:
        if self.esta_vencido():
            raise MedicamentoVencidoException(self._nombre, self._fecha_vencimiento)
        return True
