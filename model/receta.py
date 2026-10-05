class Receta:
    def __init__(self, numero_folio: str, medico: str, retenida: bool = False):
        self._numero_folio = numero_folio
        self._medico = medico
        self._retenida = retenida
        self._autorizada_por_quimico = False

    @property
    def numero_folio(self) -> str:
        return self._numero_folio

    @property
    def medico(self) -> str:
        return self._medico

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
