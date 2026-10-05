from model.medicamento import Medicamento
from model.excepciones import VentaNoAutorizadaException, RecetaInvalidaException


class MedRecetaControlado(Medicamento):
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False, requiere_retencion: bool = True):
        super().__init__(nombre, precio_base, stock, fecha_vencimiento, es_importado)
        self._requiere_retencion = requiere_retencion

    @property
    def requiere_retencion(self) -> bool:
        return self._requiere_retencion

    def validar_venta(self, receta=None) -> bool:
        super().validar_venta(receta)

        if receta is None or not receta.es_valida():
            raise RecetaInvalidaException(f"Venta rechazada: '{self.nombre}' requiere receta medica valida.")

        if self._requiere_retencion and not receta.retenida:
            raise VentaNoAutorizadaException(f"Venta rechazada: El medicamento controlado '{self.nombre}' requiere retencion de receta.")

        if not receta.autorizada_por_quimico:
            raise VentaNoAutorizadaException(f"Venta rechazada: El medicamento controlado '{self.nombre}' requiere autorizacion de un Quimico Farmaceutico.")

        return True
