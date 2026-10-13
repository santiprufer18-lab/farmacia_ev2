from model.medicamento import Medicamento


class MedSinReceta(Medicamento):
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False, id_medicamento: int = None):
        super().__init__(nombre, precio_base, stock, fecha_vencimiento, es_importado, id_medicamento)

    @property
    def tipo_medicamento(self) -> str:
        return "LIBRE"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente que este medicamento no requiere receta."""
        return "NINGUNA"

    def validar_venta(self, receta=None) -> bool:
        super().validar_venta(receta)
        return True
