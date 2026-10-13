from model.medicamento import Medicamento
from model.excepciones import VentaNoAutorizadaException, RecetaInvalidaException


class MedRecetaControlado(Medicamento):
    def __init__(self, nombre: str, precio_base: float, stock: int, fecha_vencimiento: str, es_importado: bool = False, requiere_retencion: bool = True, id_medicamento: int = None):
        super().__init__(nombre, precio_base, stock, fecha_vencimiento, es_importado, id_medicamento)
        self._requiere_retencion = bool(requiere_retencion)

    @property
    def tipo_medicamento(self) -> str:
        return "CONTROLADO"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente que este medicamento requiere receta controlada con retencion y autorizacion QF."""
        return "RECETA_CONTROLADA"

    @property
    def requiere_retencion(self) -> bool:
        return self._requiere_retencion

    @requiere_retencion.setter
    def requiere_retencion(self, valor: bool):
        self._requiere_retencion = bool(valor)

    def validar_venta(self, receta=None) -> bool:
        super().validar_venta(receta)
        if receta is None or not receta.es_valida():
            raise RecetaInvalidaException(
                f"Venta rechazada: '{self.nombre}' requiere receta medica valida."
            )
        if self._requiere_retencion and not receta.retenida:
            raise VentaNoAutorizadaException(
                f"Venta rechazada: El medicamento controlado '{self.nombre}' requiere retencion de receta."
            )
        if not receta.autorizada_por_quimico:
            raise VentaNoAutorizadaException(
                f"Venta rechazada: El medicamento controlado '{self.nombre}' requiere autorizacion de un Quimico Farmaceutico."
            )
        return True
