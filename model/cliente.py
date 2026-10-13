class Cliente:
    def __init__(self, rut: str, nombre: str, id_cliente: int = None):
        self._id_cliente = id_cliente
        self.rut = rut
        self.nombre = nombre

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor: int):
        self._id_cliente = valor

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str):
        if not valor:
            raise ValueError("El RUT no puede estar vacio.")
        val_limpio = str(valor).replace(".", "").replace("-", "").strip().upper()
        if len(val_limpio) < 8 or len(val_limpio) > 9:
            raise ValueError(f"RUT de cliente '{valor}' no es valido (debe tener entre 7 y 8 digitos mas digito verificador).")
        cuerpo = val_limpio[:-1]
        dv = val_limpio[-1]
        if not cuerpo.isdigit() or (not dv.isdigit() and dv != "K"):
            raise ValueError(f"RUT de cliente '{valor}' contiene caracteres invalidos.")
        
        # Algoritmo de validacion de RUT chileno (modulo 11)
        suma = 0
        multiplicador = 2
        for d in reversed(cuerpo):
            suma += int(d) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1
        resto = 11 - (suma % 11)
        dv_esperado = "K" if resto == 10 else ("0" if resto == 11 else str(resto))
        if dv != dv_esperado:
            raise ValueError(f"RUT de cliente '{valor}' no coincide con su digito verificador.")

        # Guardar en formato estandar XX.XXX.XXX-X
        cuerpo_fmt = f"{int(cuerpo):,}".replace(",", ".")
        self._rut = f"{cuerpo_fmt}-{dv}"

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre del cliente no puede estar vacio.")
        if len(str(valor).strip()) < 3:
            raise ValueError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = str(valor).strip()

    def validar_rut(self) -> bool:
        return bool(self._rut)
