"""
Módulo de Auditoría y Registro de Eventos de Seguridad de la Farmacia.
"""

from datetime import datetime


class AuditoriaService:
    """
    Servicio de registro de auditoría para auditorías de seguridad y control de excepciones.
    """
    _log_eventos = []

    @classmethod
    def registrar_evento(cls, tipo: str, detalle: str, usuario: str = "Sistema"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        registro = {
            "fecha": timestamp,
            "tipo": tipo,
            "detalle": detalle,
            "usuario": usuario
        }
        cls._log_eventos.append(registro)

    @classmethod
    def obtener_historial(cls) -> list:
        return cls._log_eventos
