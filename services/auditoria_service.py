from datetime import datetime
from dao.database import obtener_conexion


class AuditoriaService:
    """Servicio de registro y persistencia de eventos de auditoria y seguridad del sistema."""

    @classmethod
    def registrar_evento(cls, tipo: str, detalle: str, usuario: str = "Sistema"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO auditoria (fecha, tipo, detalle, usuario)
                    VALUES (?, ?, ?, ?)
                """, (timestamp, tipo, detalle, usuario))
                conn.commit()
        except Exception as e:
            print(f"[AUDITORIA ERROR] No se pudo guardar el evento en base de datos: {e}")

    @classmethod
    def obtener_historial(cls) -> list:
        try:
            with obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM auditoria ORDER BY id_evento DESC LIMIT 50")
                filas = cursor.fetchall()
                return [
                    {
                        "id": f["id_evento"],
                        "fecha": f["fecha"],
                        "tipo": f["tipo"],
                        "detalle": f["detalle"],
                        "usuario": f["usuario"]
                    }
                    for f in filas
                ]
        except Exception:
            return []
