"""
Modulo de Excepciones Personalizadas del Dominio de Farmacia.
"""

class MedicamentoVencidoException(Exception):
    """Excepcion lanzada cuando se intenta vender un medicamento vencido."""
    def __init__(self, nombre_medicamento: str, fecha_vencimiento: str):
        self.nombre_medicamento = nombre_medicamento
        self.fecha_vencimiento = fecha_vencimiento
        super().__init__(f"No se puede vender '{nombre_medicamento}': se encuentra vencido desde {fecha_vencimiento}.")


class RecetaInvalidaException(Exception):
    """Excepcion lanzada cuando una receta medica no es valida o falta para el medicamento."""
    def __init__(self, mensaje: str = "La receta medica proporcionada no es valida o no existe."):
        super().__init__(mensaje)


class VentaNoAutorizadaException(Exception):
    """Excepcion lanzada cuando una venta de medicamento controlado no cuenta con la autorizacion requerida."""
    def __init__(self, mensaje: str = "Venta rechazada: Medicamento controlado requiere receta retenida y autorizacion de un Quimico Farmaceutico."):
        super().__init__(mensaje)
