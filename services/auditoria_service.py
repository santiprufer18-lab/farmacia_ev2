
from datetime import datetime


class AuditoriaService:
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
