"""
Módulo de Excepciones Personalizadas del Dominio de Farmacia.
"""

class MedicamentoVencidoException(Exception):
    """Excepción lanzada cuando se intenta vender un medicamento vencido."""
    def __init__(self, nombre_medicamento: str, fecha_vencimiento: str):
        self.nombre_medicamento = nombre_medicamento
        self.fecha_vencimiento = fecha_vencimiento
        super().__init__(f"No se puede vender '{nombre_medicamento}': se encuentra vencido desde {fecha_vencimiento}.")


class RecetaInvalidaException(Exception):
    """Excepción lanzada cuando una receta médica no es válida o falta para el medicamento."""
    def __init__(self, mensaje: str = "La receta médica proporcionada no es válida o no existe."):
        super().__init__(mensaje)


class VentaNoAutorizadaException(Exception):
    """Excepción lanzada cuando una venta de medicamento controlado no cuenta con la autorización requerida."""
    def __init__(self, mensaje: str = "Venta rechazada: Medicamento controlado requiere receta retenida y autorización de un Químico Farmacéutico."):
        super().__init__(mensaje)
