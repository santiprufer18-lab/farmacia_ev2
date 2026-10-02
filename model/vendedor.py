from model.personal import Personal


class Vendedor(Personal):
    """
    Representa a un trabajador vendedor asignado a una caja.
    """
    def __init__(self, rut: str, nombre: str, caja_asignada: int):
        super().__init__(rut, nombre)
        self.caja_asignada = caja_asignada

    @property
    def caja_asignada(self) -> int:
        return self._caja_asignada

    @caja_asignada.setter
    def caja_asignada(self, numero: int):
        if numero <= 0:
            raise ValueError("El número de caja asignada debe ser mayor a 0.")
        self._caja_asignada = int(numero)

    def atender_cliente(self, cliente_nombre: str) -> str:
        return f"Vendedor {self.nombre} atendiendo al cliente {cliente_nombre} en caja {self._caja_asignada}."
