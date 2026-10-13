from model.personal import Personal


class Vendedor(Personal):
    def __init__(self, rut: str, nombre: str, caja_asignada: int, id_vendedor: int = None):
        super().__init__(rut, nombre)
        self._id_vendedor = id_vendedor
        self.caja_asignada = caja_asignada

    @property
    def id_vendedor(self) -> int:
        return self._id_vendedor

    @id_vendedor.setter
    def id_vendedor(self, valor: int):
        self._id_vendedor = valor

    @property
    def caja_asignada(self) -> int:
        return self._caja_asignada

    @caja_asignada.setter
    def caja_asignada(self, numero: int):
        try:
            val_num = int(numero)
        except (ValueError, TypeError):
            raise ValueError("El numero de caja debe ser un entero.")
        if val_num <= 0:
            raise ValueError("El numero de caja asignada debe ser mayor a 0.")
        self._caja_asignada = val_num

    def atender_cliente(self, cliente_nombre: str) -> str:
        return f"Vendedor {self.nombre} atendiendo al cliente {cliente_nombre} en caja {self._caja_asignada}."
