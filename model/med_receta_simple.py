from model.medicamento import Medicamento
from model.excepciones import RecetaInvalidaException


class MedRecetaSimple(Medicamento):
    """
    Representa medicamentos que requieren la presentación de una receta médica simple.
    """
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False):
        super().__init__(nombre, precio_base, stock, fecha_vencimiento, es_importado)

    def validar_venta(self, receta=None) -> bool:
        """
        Sobrescribe el método polimórfico: valida que exista una receta médica y que sea válida.
        """
        # Verifica vencimiento llamando a la superclase
        super().validar_venta(receta)

        if receta is None or not receta.es_valida():
            raise RecetaInvalidaException(f"Venta no permitida: El medicamento '{self.nombre}' requiere receta médica simple válida.")
        
        return True
