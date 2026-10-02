from model.medicamento import Medicamento


class MedSinReceta(Medicamento):
    """
    Representa medicamentos de venta libre que no requieren receta médica.
    """
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False):
        super().__init__(nombre, precio_base, stock, fecha_vencimiento, es_importado)

    def validar_venta(self, receta=None) -> bool:
        """
        Sobrescribe el método polimórfico: no exige receta, solo verifica vencimiento y stock.
        """
        # Verifica vencimiento llamando al comportamiento base
        super().validar_venta(receta)
        return True
