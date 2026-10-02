from model.personal import Personal
from model.receta import Receta


class QuimicoFarmaceutico(Personal):
    """
    Representa al profesional farmacéutico facultado para autorizar medicamentos controlados.
    """
    def __init__(self, rut: str, nombre: str, num_registro: str):
        super().__init__(rut, nombre)
        self._num_registro = num_registro

    @property
    def num_registro(self) -> str:
        return self._num_registro

    def autorizar_controlado(self, receta: Receta) -> bool:
        """Autoriza una receta retenida para permitir la venta de medicamentos controlados."""
        if receta and receta.es_valida() and receta.retenida:
            receta.autorizada_por_quimico = True
            return True
        return False
