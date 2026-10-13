# Evaluacion Sumativa Nro. 3: Software Orientado a Objetos, Persistencia y Seguridad en Python

## 1. Integrantes y Negocio

### Integrantes del Equipo
* Integrante 1: Santiago Prufer (santi.prufer@inacapmail.cl
* Integrante 1: Bastian Flores (bastian.flores38@inacapmail.cl))

* Asignatura: Programacion Orientada a Objeto Seguro (TI3V21)
* Seccion: 114-2B-F1
* Sede: Puente Alto, INACAP

### Giro del Negocio: Farmacia Cruz del Sur S.A.
Farmacia Cruz del Sur S.A. es una cadena farmaceutica comunitaria y asistencial dedicada a la dispensacion informada de medicamentos y productos sanitarios. El sistema informatico gestiona:
1. Terminal de punto de venta (POS) y facturacion electronica con desglose de IVA y calculo en pesos chilenos (CLP).
2. Catalogo y clasificacion regulatoria de medicamentos (Venta Libre, Receta Simple y Medicamentos Psicotropicos/Estupefacientes Controlados con retencion y visto bueno del Quimico Farmaceutico).
3. Medicamentos importados con cotizacion en dolares (USD) recalculados dinamicamente a moneda nacional mediante servicios web financieros.
4. Persistencia relacional de inventario, clientes, ventas y bitacora de auditoria sobre base de datos SQLite.


## 2. Como Instalar y Ejecutar el Programa, Paso a Paso, desde un Computador que Solo Tiene Python

El sistema esta disenado para ser completamente portable y autoejecutable. No requiere software adicional ni configuracion previa de bases de datos, ya que SQLite esta integrado de forma nativa en el interprete de Python y las tablas se crean de forma automatica en el primer arranque.

### Paso 1: Clonar o descargar el repositorio
Abra una terminal (PowerShell, Command Prompt o Bash) y clone el repositorio:
```bash
git clone https://github.com/santiprufer18-lab/farmacia_ev2.git
cd farmacia_ev2
```
(O ingrese a la carpeta del proyecto descargado).

### Paso 2: Crear y activar un entorno virtual (Recomendado)
Para asegurar el aislamiento de paquetes:

* En Windows (PowerShell):
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* En Linux o macOS:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Paso 3: Instalar las dependencias oficiales requeridas
El proyecto utiliza la libreria oficial `requests` para el consumo HTTP resiliente de las APIs:
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la aplicacion
Inicie el programa ejecutando el archivo principal:
```bash
python main.py
```
Al iniciar, el sistema verificara la existencia de la base de datos relacional `farmacia.db`. Si no existe, creara automaticamente las tablas (`clientes`, `medicamentos`, `vendedores`, `quimicos`, `ventas`, `detalles_venta`, `auditoria`) e insertara el catalogo y personal inicial, quedando listo para operar de inmediato.


---

## 3. Decisiones de Seguridad

### A. Prevencion de Inyeccion SQL (SQL Injection)
Para anular cualquier riesgo de inyeccion SQL (CWE-89), se aplico una estricta separacion de responsabilidades mediante el patron Data Access Object (DAO) y las siguientes directrices tecnicas:
1. **Parametrizacion Total de Consultas**: El 100% de las sentencias SQL ejecutadas en la base de datos utilizan marcadores posicionales (`?`) proporcionados por la libreria oficial `sqlite3`. Los parametros ingresados por los usuarios jamas se interpolan mediante concatenacion de texto (`+`), f-strings (`f"..."`) o metodos de formato (`.format()`).
   * Ejemplo implementado en `MedicamentoDAO`:
     ```python
     # Consulta segura implementada
     cursor.execute(
         "INSERT INTO medicamentos (nombre, precio_base, stock, fecha_vencimiento, es_importado, tipo_medicamento, requiere_retencion) VALUES (?, ?, ?, ?, ?, ?, ?)",
         (med.nombre, med.precio_base, med.stock, med.fecha_vencimiento, 1 if med.es_importado else 0, med.tipo_medicamento, requiere_ret)
     )
     ```
2. **Uso de Transacciones Atomicas**: En el registro de ventas (`VentaDAO.registrar_venta`), la cabecera y todas las lineas de detalle se procesan dentro de una transaccion atomica con `BEGIN TRANSACTION` y confirmacion explicita (`conn.commit()`). Ante cualquier error de integridad o excepcion, se ejecuta un `conn.rollback()`, garantizando consistencia ACID.
3. **Aislamiento Arquitectonico**: Ninguna clase de la capa de dominio (`model/`) contiene instrucciones SQL ni referencias a la persistencia. La logica de acceso a datos reside exclusivamente en `dao/`.

### B. Validacion Exhaustiva de Entradas de Usuario
Todas las entradas proporcionadas por los operadores se validan en tres dimensiones antes de cualquier operacion:
1. **Tipo**: Se valida la conversion de datos para evitar caidas imprevistas (`int`, `float`, `str`). Si el usuario ingresa caracteres no numericos donde se espera un numero, la entrada es rechazada con mensaje explicativo y se solicita nuevamente sin detener el programa.
2. **Formato**:
   * **RUT Chileno**: En la clase `Cliente` y en las funciones de captura, se valida la estructura del RUT mediante expresiones y el algoritmo oficial de verificacion Modulo 11. Se rechazan RUTs con digito verificador inconsistente o caracteres anomalos.
   * **Fechas**: La fecha de vencimiento se valida bajo el formato estricto `AAAA-MM-DD` mediante `datetime.strptime()`, asegurando anio, mes y dia validos en el calendario.
3. **Rango**:
   * Precios base deben ser estrictamente mayores a 0 (`precio_base > 0`).
   * Cantidades en compras deben ser al menos 1 (`cantidad >= 1`).
   * Stock fisico no puede ser negativo (`stock >= 0`).
   * Rango de opciones de menu restringido a los indices validos.
4. **Validacion en Setters del Modelo**: El encapsulamiento en las clases `Cliente`, `Medicamento`, `Vendedor` y `DetalleVenta` garantiza que cualquier asignacion invalida de atributos lance excepciones controladas (`ValueError`), asegurando que ningun estado corrupto pueda persistir en memoria ni en base de datos.
5. **Tolerancia a Fallos y Continuidad de la Aplicacion**: Ante cualquier dato invalido o excepcion de negocio (`MedicamentoVencidoException`, `RecetaInvalidaException`, `VentaNoAutorizadaException`), el sistema captura la excepcion, informa al usuario el motivo del rechazo y continua en ejecucion sin caidas de proceso.


---

## 4. Uso de Inteligencia Artificial

Durante el desarrollo de esta evaluacion se consultaron herramientas de asistencia de inteligencia artificial para apoyar el diseno y refactorizacion de modulos de seguridad y persistencia.

### Ejemplo Concreto: Refactorizacion del Consumo de API Externa

#### 1. Codigo Inicialmente Sugerido por la IA
La IA sugirio inicialmente la siguiente funcion generica para obtener el valor del dolar:

```python
# Codigo sugerido por la IA (Inseguro y no resiliente)
import urllib.request
import json

def get_dolar():
    try:
        res = urllib.request.urlopen("https://mindicador.cl/api/dolar")
        data = json.loads(res.read())
        return data["serie"][0]["valor"]
    except:
        return 950.0
```

#### 2. Razon Tecnica de Rechazo y Modificacion
El codigo sugerido presentaba graves deficiencias tecnicas y de ciberseguridad:
* **Falta de Timeout**: `urllib.request.urlopen` sin parametro de timeout puede dejar el hilo de ejecucion bloqueado indefinidamente si el servidor remoto congela la conexion TCP, provocando una denegacion de servicio (DoS) local.
* **Uso de Libreria Inadecuada**: La rubrica exige especificamente la utilizacion de la libreria oficial `requests` para el consumo HTTP.
* **Excepcion Silenciosa (Bare Except)**: Capturar con un `except:` ciego sin registrar ni diferenciar el error oculta fallos criticos de red, certificados SSL caducados o respuestas corruptas, impidiendo la trazabilidad del sistema.
* **Vulnerabilidad de User-Agent**: No definir cabeceras puede causar bloqueos preventivos por cortafuegos de aplicaciones web (WAF).

#### 3. Codigo Final Adoptado en el Proyecto (`services/api_service.py`)
Se refactorizo la propuesta implementando un cliente HTTP robusto con gestion diferenciada de errores, timeout explicito y registro de auditoria:

```python
# Codigo adoptado con criterios de seguridad y resiliencia
import requests
from services.auditoria_service import AuditoriaService

class APIService:
    VALOR_DOLAR_FALLBACK = 950.0
    TIMEOUT_SEGUNDOS = 5

    @classmethod
    def obtener_dolar_tiempo_real(cls) -> float:
        url = "https://mindicador.cl/api/dolar"
        headers = {"User-Agent": "FarmaciaCruzDelSur/1.0 (Windows NT 10.0; Win64; x64)"}
        try:
            respuesta = requests.get(url, headers=headers, timeout=cls.TIMEOUT_SEGUNDOS)
            if respuesta.status_code != 200:
                print(f"[AVISO SERVICIO EXTERNO] Codigo HTTP {respuesta.status_code}. Usando tasa de contingencia.")
                return cls.VALOR_DOLAR_FALLBACK

            datos = respuesta.json()
            if "serie" not in datos or not datos["serie"] or "valor" not in datos["serie"][0]:
                print("[AVISO SERVICIO EXTERNO] Formato JSON inesperado. Usando tasa de contingencia.")
                return cls.VALOR_DOLAR_FALLBACK

            valor_dolar = float(datos["serie"][0]["valor"])
            AuditoriaService.registrar_evento("API_DOLAR_EXITO", f"USD: ${valor_dolar:,.2f} CLP.")
            return valor_dolar

        except requests.exceptions.Timeout:
            print(f"[AVISO SERVICIO EXTERNO] Tiempo de espera agotado ({cls.TIMEOUT_SEGUNDOS}s). Usando tasa de contingencia.")
            AuditoriaService.registrar_evento("API_DOLAR_TIMEOUT", "Timeout al consultar mindicador.cl.")
            return cls.VALOR_DOLAR_FALLBACK
        except requests.exceptions.ConnectionError:
            print("[AVISO SERVICIO EXTERNO] Sin conexion a Internet. Usando tasa de contingencia.")
            AuditoriaService.registrar_evento("API_DOLAR_SIN_CONEXION", "Fallo de red al consultar mindicador.cl.")
            return cls.VALOR_DOLAR_FALLBACK
        except requests.exceptions.RequestException as e:
            print(f"[AVISO SERVICIO EXTERNO] Error de peticion HTTP: {e}. Usando tasa de contingencia.")
            return cls.VALOR_DOLAR_FALLBACK
```
Con esta decision tecnica, el sistema garantiza alta disponibilidad y continuidad del negocio aun ante caidas completas de conectividad externa.


---

## 5. Refactorizacion Orientada a Objetos: Eliminacion de `isinstance` mediante Polimorfismo

Para cumplir estrictamente con los principios de diseno SOLID (especificamente el Principio Abierto/Cerrado - OCP) y evitar el anti-patron de verificar tipos con `isinstance`, se refactorizo la jerarquia de `Medicamento` y el modulo `main.py`:

1. **Propiedad Polimorfica `tipo_receta_requerida`**:
   - `MedSinReceta`: retorna `"NINGUNA"`.
   - `MedRecetaSimple`: retorna `"RECETA_SIMPLE"`.
   - `MedRecetaControlado`: retorna `"RECETA_CONTROLADA"`.
2. **Despacho Polimorfico en `main.py`**:
   - Se reemplazaron todas las llamadas `isinstance(med_sel, MedRecetaSimple)` e `isinstance(med_sel, MedRecetaControlado)` consultando directamente `med_sel.tipo_receta_requerida`.
   - Se elimino el acoplamiento y la necesidad de importar subclases para validaciones de tipo en la terminal de venta.
3. **Propiedad `requiere_retencion` en Dominio y Persistencia**:
   - En `MedicamentoDAO`, se elimino `isinstance(med, MedRecetaControlado)` delegando la consulta directamente a la propiedad polimorfica `med.requiere_retencion`.
4. **Verificacion y Capturas Reales**:
   - Se desarrollo la suite de pruebas `test_polimorfismo.py` validando los 5 escenarios criticos (venta libre, receta simple, controlado sin/con autorizacion QF, y medicamentos vencidos).
   - El detalle completo con comparativa de codigo y capturas reales de terminal se encuentra en el archivo [DOCUMENTACION_POLIMORFISMO.md](file:///C:/Users/youngnaxitoo/Downloads/farmacia_extracted/farmacia_ev3/DOCUMENTACION_POLIMORFISMO.md).

