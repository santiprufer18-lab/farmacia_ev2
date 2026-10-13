from model.personal import Personal
from model.receta import Receta


class QuimicoFarmaceutico(Personal):
    def __init__(self, rut: str, nombre: str, num_registro: str, id_quimico: int = None):
        super().__init__(rut, nombre)
        self._id_quimico = id_quimico
        self.num_registro = num_registro

    @property
    def id_quimico(self) -> int:
        return self._id_quimico

    @id_quimico.setter
    def id_quimico(self, valor: int):
        self._id_quimico = valor

    @property
    def num_registro(self) -> str:
        return self._num_registro

    @num_registro.setter
    def num_registro(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El numero de registro sanitario del Quimico no puede estar vacio.")
        self._num_registro = str(valor).strip()

    def autorizar_controlado(self, receta: Receta) -> bool:
        if receta and receta.es_valida() and receta.retenida:
            receta.autorizada_por_quimico = True
            return True
        return False
