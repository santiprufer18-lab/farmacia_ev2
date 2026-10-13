class Personal:
    def __init__(self, rut: str, nombre: str):
        self.rut = rut
        self.nombre = nombre

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str):
        if not valor:
            raise ValueError("El RUT no puede estar vacio.")
        val_limpio = str(valor).replace(".", "").replace("-", "").strip().upper()
        if len(val_limpio) < 8 or len(val_limpio) > 9:
            raise ValueError("El RUT ingresado no es valido.")
        cuerpo = val_limpio[:-1]
        dv = val_limpio[-1]
        if not cuerpo.isdigit() or (not dv.isdigit() and dv != "K"):
            raise ValueError("El RUT contiene caracteres invalidos.")
        cuerpo_fmt = f"{int(cuerpo):,}".replace(",", ".")
        self._rut = f"{cuerpo_fmt}-{dv}"

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre no puede estar vacio.")
        self._nombre = str(valor).strip()
