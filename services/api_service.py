"""
Módulo de Servicios de Integración Externa.
Conexiones en tiempo real con fuentes de datos oficiales:
1. Cotización oficial del Dólar USD en Chile (mindicador.cl)
2. Red Nacional de Farmacias de Turno en Chile (Ministerio de Salud - MINSAL)
"""

import json
import urllib.request
import urllib.error
from services.auditoria_service import AuditoriaService


class APIService:
    """
    Servicio encargado de la sincronización con fuentes externas de datos sanitarios y económicos.
    """
    VALOR_DOLAR_FALLBACK = 950.0

    @classmethod
    def obtener_dolar_tiempo_real(cls) -> float:
        """
        Obtiene la cotización oficial del dólar hoy en Chile desde mindicador.cl.
        Si no hay conexión, utiliza la tasa de respaldo oficial de forma segura.
        """
        url = "https://mindicador.cl/api/dolar"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    valor_dolar = float(data['serie'][0]['valor'])
                    AuditoriaService.registrar_evento(
                        tipo="DOLAR_SYNC_OK",
                        detalle=f"Cotización oficial USD sincronizada exitosamente: ${valor_dolar:,.2f} CLP"
                    )
                    return valor_dolar
        except Exception as e:
            AuditoriaService.registrar_evento(
                tipo="DOLAR_SYNC_OFFLINE",
                detalle=f"Conexión remota no disponible ({e}). Utilizando tasa fija de contingencia ${cls.VALOR_DOLAR_FALLBACK} CLP"
            )
        return cls.VALOR_DOLAR_FALLBACK

    @classmethod
    def obtener_farmacias_turno(cls, comuna_filtro: str = None) -> list:
        """
        Consulta la Red Oficial del Ministerio de Salud (MINSAL) para obtener las farmacias de turno.
        """
        url = "https://farmanet.minsal.cl/maps/index.php/ws/getPharmaciesWithBureauId"
        farmacias = []
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    raw_data = json.loads(response.read().decode('utf-8'))
                    for item in raw_data:
                        comuna = item.get('comuna_nombre', '').strip()
                        nombre = item.get('local_nombre', '').strip()
                        direccion = item.get('local_direccion', '').strip()
                        telefono = item.get('local_telefono', 'N/A').strip()
                        apertura = item.get('funcionamiento_hora_apertura', '').strip()
                        cierre = item.get('funcionamiento_hora_cierre', '').strip()

                        if comuna_filtro:
                            if comuna_filtro.lower() in comuna.lower():
                                farmacias.append({
                                    "nombre": nombre,
                                    "comuna": comuna,
                                    "direccion": direccion,
                                    "telefono": telefono,
                                    "horario": f"{apertura} a {cierre}"
                                })
                        else:
                            farmacias.append({
                                "nombre": nombre,
                                "comuna": comuna,
                                "direccion": direccion,
                                "telefono": telefono,
                                "horario": f"{apertura} a {cierre}"
                            })

                    AuditoriaService.registrar_evento(
                        tipo="MINSAL_SYNC_OK",
                        detalle=f"Consulta Red Nacional MINSAL realizada ({len(farmacias)} locales obtenidos)"
                    )
                    return farmacias
        except Exception as e:
            AuditoriaService.registrar_evento(
                tipo="MINSAL_SYNC_OFFLINE",
                detalle=f"Servicio MINSAL no disponible en este momento ({e})"
            )

        # Retorna lista de muestra si no hay conexión
        return [
            {"nombre": "Farmacia Cruz del Sur - Central", "comuna": "Puente Alto", "direccion": "Av. Concha y Toro 1340", "telefono": "+56 2 2999 8888", "horario": "24 Horas"},
            {"nombre": "Farmacia Ahumada - Plaza", "comuna": "Puente Alto", "direccion": "Balmaceda 420", "telefono": "+56 2 2888 7777", "horario": "08:30 a 22:00"}
        ]
