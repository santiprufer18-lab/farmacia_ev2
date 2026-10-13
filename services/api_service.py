import requests
from services.auditoria_service import AuditoriaService


class APIService:
    """
    Servicio centralizado para consumo de APIs externas utilizando la libreria requests.
    Maneja tiempos de espera (timeout), fallos de conexion, respuestas inesperadas
    y garantiza la continuidad operativa del sistema sin detener la ejecucion.
    """

    VALOR_DOLAR_FALLBACK = 950.0
    TIMEOUT_SEGUNDOS = 5

    @classmethod
    def obtener_dolar_tiempo_real(cls) -> float:
        """
        Consulta la API publica de mindicador.cl para obtener la cotizacion del dolar en tiempo real.
        Aplica un tiempo maximo de espera y gestiona excepciones especificas para asegurar continuidad.
        """
        url = "https://mindicador.cl/api/dolar"
        headers = {"User-Agent": "FarmaciaCruzDelSur/1.0 (Windows NT 10.0; Win64; x64)"}

        try:
            respuesta = requests.get(url, headers=headers, timeout=cls.TIMEOUT_SEGUNDOS)

            # Validar codigo de estado HTTP
            if respuesta.status_code != 200:
                print(f"\n[AVISO SERVICIO EXTERNO] La API de mindicador.cl respondio con codigo HTTP {respuesta.status_code}.")
                print(f"[CONTINUIDAD OPERATIVA] Se utilizara el valor de respaldo fijado en ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
                AuditoriaService.registrar_evento(
                    tipo="API_DOLAR_HTTP_ERROR",
                    detalle=f"Respuesta HTTP {respuesta.status_code} desde mindicador.cl. Usando fallback."
                )
                return cls.VALOR_DOLAR_FALLBACK

            # Parseo y validacion de la estructura esperada
            datos = respuesta.json()
            if "serie" not in datos or not datos["serie"] or "valor" not in datos["serie"][0]:
                print("\n[AVISO SERVICIO EXTERNO] Estructura de respuesta inesperada desde la API de mindicador.cl.")
                print(f"[CONTINUIDAD OPERATIVA] Se utilizara el valor de respaldo fijado en ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
                AuditoriaService.registrar_evento(
                    tipo="API_DOLAR_FORMAT_ERROR",
                    detalle="La estructura JSON de mindicador.cl no contiene el campo 'serie[0].valor'. Usando fallback."
                )
                return cls.VALOR_DOLAR_FALLBACK

            valor_dolar = float(datos["serie"][0]["valor"])
            AuditoriaService.registrar_evento(
                tipo="API_DOLAR_EXITO",
                detalle=f"Cotizacion oficial USD obtenida exitosamente: ${valor_dolar:,.2f} CLP."
            )
            return valor_dolar

        except requests.exceptions.Timeout:
            print(f"\n[AVISO SERVICIO EXTERNO] Tiempo de espera agotado ({cls.TIMEOUT_SEGUNDOS}s) al consultar la API externa de mindicador.cl.")
            print(f"[CONTINUIDAD OPERATIVA] La API tardo demasiado. Se activa tasa de contingencia: ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
            AuditoriaService.registrar_evento(
                tipo="API_DOLAR_TIMEOUT",
                detalle=f"Timeout de {cls.TIMEOUT_SEGUNDOS} segundos alcanzado al consultar mindicador.cl. Usando fallback."
            )
            return cls.VALOR_DOLAR_FALLBACK

        except requests.exceptions.ConnectionError:
            print("\n[AVISO SERVICIO EXTERNO] Sin conexion con el servicio de mindicador.cl (equipo sin conexion a red o servidor no disponible).")
            print(f"[CONTINUIDAD OPERATIVA] Se activa tasa de contingencia: ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
            AuditoriaService.registrar_evento(
                tipo="API_DOLAR_SIN_CONEXION",
                detalle="Fallo de conexion de red al consultar mindicador.cl. Usando fallback."
            )
            return cls.VALOR_DOLAR_FALLBACK

        except requests.exceptions.RequestException as req_err:
            print(f"\n[AVISO SERVICIO EXTERNO] Error de peticion al consumir la API externa: {req_err}")
            print(f"[CONTINUIDAD OPERATIVA] Se activa tasa de contingencia: ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
            AuditoriaService.registrar_evento(
                tipo="API_DOLAR_REQUEST_EXCEPTION",
                detalle=f"Error generico de requests: {req_err}. Usando fallback."
            )
            return cls.VALOR_DOLAR_FALLBACK

        except (ValueError, KeyError, IndexError) as parse_err:
            print(f"\n[AVISO SERVICIO EXTERNO] Error al interpretar la respuesta JSON de la API: {parse_err}")
            print(f"[CONTINUIDAD OPERATIVA] Se activa tasa de contingencia: ${cls.VALOR_DOLAR_FALLBACK:,.2f} CLP.")
            AuditoriaService.registrar_evento(
                tipo="API_DOLAR_PARSE_ERROR",
                detalle=f"Error interpretando datos JSON: {parse_err}. Usando fallback."
            )
            return cls.VALOR_DOLAR_FALLBACK

    @classmethod
    def obtener_farmacias_turno(cls, comuna_filtro: str = None) -> list:
        """
        Consulta la red nacional de farmacias de turno del MINSAL utilizando requests.
        Maneja errores de red y devuelve lista vacia o datos locales ante contingencias.
        """
        url = "https://farmanet.minsal.cl/maps/index.php/ws/getPharmaciesWithBureauId"
        headers = {"User-Agent": "FarmaciaCruzDelSur/1.0 (Windows NT 10.0; Win64; x64)"}
        farmacias = []

        try:
            resp = requests.get(url, headers=headers, timeout=cls.TIMEOUT_SEGUNDOS)
            if resp.status_code == 200:
                raw_data = resp.json()
                for item in raw_data:
                    comuna = item.get("comuna_nombre", "").strip()
                    nombre = item.get("local_nombre", "").strip()
                    direccion = item.get("local_direccion", "").strip()
                    telefono = item.get("local_telefono", "N/A").strip()
                    apertura = item.get("funcionamiento_hora_apertura", "").strip()
                    cierre = item.get("funcionamiento_hora_cierre", "").strip()

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
                    tipo="API_MINSAL_EXITO",
                    detalle=f"Consulta MINSAL completada con {len(farmacias)} locales obtenidos."
                )
                return farmacias

        except Exception as e:
            AuditoriaService.registrar_evento(
                tipo="API_MINSAL_OFFLINE",
                detalle=f"Servicio MINSAL no disponible ({e}). Utilizando datos locales de contingencia."
            )

        # Contingencia local si el servicio de MINSAL esta caido
        return [
            {
                "nombre": "Farmacia Cruz del Sur - Central",
                "comuna": "Puente Alto",
                "direccion": "Av. Concha y Toro 1340",
                "telefono": "+56 2 2999 8888",
                "horario": "24 Horas"
            },
            {
                "nombre": "Farmacia Ahumada - Plaza",
                "comuna": "Puente Alto",
                "direccion": "Balmaceda 420",
                "telefono": "+56 2 2888 7777",
                "horario": "08:30 a 22:00"
            }
        ]
