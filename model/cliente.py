class Cliente:
    def __init__(self, rut: str, nombre: str):
        self.rut = rut        # Usa setter con validación
        self._nombre = nombre

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str):
        val_limpio = str(valor).replace(".", "").replace("-", "").strip()
        if len(val_limpio) < 8 or len(val_limpio) > 10:
            raise ValueError(f"RUT de cliente '{valor}' no es valido (debe tener entre 8 y 9 digitos mas DV).")
        self._rut = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    def validar_rut(self) -> bool:
        return len(self._rut) > 0
