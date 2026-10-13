class Receta:
    def __init__(self, numero_folio: str, medico: str, retenida: bool = False, autorizada_por_quimico: bool = False, id_receta: int = None):
        self._id_receta = id_receta
        self.numero_folio = numero_folio
        self.medico = medico
        self._retenida = bool(retenida)
        self._autorizada_por_quimico = bool(autorizada_por_quimico)

    @property
    def id_receta(self) -> int:
        return self._id_receta

    @id_receta.setter
    def id_receta(self, valor: int):
        self._id_receta = valor

    @property
    def numero_folio(self) -> str:
        return self._numero_folio

    @numero_folio.setter
    def numero_folio(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El numero de folio de la receta no puede estar vacio.")
        self._numero_folio = str(valor).strip()

    @property
    def medico(self) -> str:
        return self._medico

    @medico.setter
    def medico(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El medico emisor de la receta no puede estar vacio.")
        self._medico = str(valor).strip()

    @property
    def retenida(self) -> bool:
        return self._retenida

    @retenida.setter
    def retenida(self, valor: bool):
        self._retenida = bool(valor)

    @property
    def autorizada_por_quimico(self) -> bool:
        return self._autorizada_por_quimico

    @autorizada_por_quimico.setter
    def autorizada_por_quimico(self, valor: bool):
        self._autorizada_por_quimico = bool(valor)

    def es_valida(self) -> bool:
        return bool(self._numero_folio and self._medico)

    def retener_receta(self):
        self._retenida = True
