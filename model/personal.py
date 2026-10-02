class Personal:
    """
    Clase base que representa a los trabajadores de la farmacia.
    """
    def __init__(self, rut: str, nombre: str):
        self.rut = rut        # Usa el setter encapsulado
        self._nombre = nombre

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str):
        val_limpio = str(valor).replace(".", "").replace("-", "").strip()
        if len(val_limpio) < 8:
            raise ValueError("El RUT ingresado no es válido.")
        self._rut = valor

    @property
    def nombre(self) -> str:
        return self._nombre
