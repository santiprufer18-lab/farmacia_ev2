# Documentación Técnica: Eliminación de `isinstance` y Aplicación de Polimorfismo Puro

**Asignatura:** Programación Orientada a Objeto Seguro (TI3V21)  
**Proyecto:** Farmacia Cruz del Sur S.A. — Evaluación Sumativa Nro. 3  
**Requerimiento del Docente:**  
> *"Saquen los isinstance de main.py, por ejemplo con un método en cada medicamento que indique qué tipo de receta requiere, y documenten el funcionamiento con capturas reales."*

---

## 1. Justificación Teórica y Arquitectónica

### El Problema de `isinstance` en POO
En la programación orientada a objetos, el uso de funciones de inspección de tipos en tiempo de ejecución como `isinstance(objeto, Clase)` dentro de la lógica de negocio o de presentación es considerado un **anti-patrón**:
1. **Violación del Principio Abierto/Cerrado (Open/Closed Principle - OCP)**: Si se agrega una nueva categoría de medicamentos (por ejemplo, `MedRecetaChequeEstupefaciente`), se tendría que buscar y modificar cada `if isinstance(...)` en `main.py` y otras capas.
2. **Acoplamiento innecesario**: La capa de presentación (`main.py`) debía importar las subclases concretas (`MedRecetaSimple`, `MedRecetaControlado`) solo para verificar tipos, perdiendo la abstracción de la interfaz `Medicamento`.
3. **Pérdida del beneficio del Polimorfismo**: En lugar de delegar al objeto la responsabilidad de conocer sus propias reglas (principio *Information Expert* de GRASP), el consumidor externo (`main.py`) asumía la decisión mediante condicionales sobre el tipo.

### La Solución Implementada: Polimorfismo Dinámico
Se definió el contrato polimórfico en la clase base `Medicamento`:
* **Propiedad `tipo_receta_requerida`**: Cada clase concreta sobrescribe esta propiedad indicando el tipo de receta que exige (`"NINGUNA"`, `"RECETA_SIMPLE"`, `"RECETA_CONTROLADA"`).
* **Propiedad `requiere_retencion`**: De igual manera, se definió en la clase base retornando `False`, y en `MedRecetaControlado` retorna el valor configurado. Con esto, también se eliminó el uso de `isinstance` en la capa de persistencia (`MedicamentoDAO`).
* En `main.py`, la interfaz interactúa con la abstracción `med_sel.tipo_receta_requerida`, sin importar ni consultar jamás la clase concreta.

---

## 2. Comparativa de Código: Antes vs. Después

### A. Subclases de Medicamento (`model/`)

#### Antes (`med_sin_receta.py`):
```python
class MedSinReceta(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "LIBRE"
```

#### Después (`med_sin_receta.py`):
```python
class MedSinReceta(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "LIBRE"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente que este medicamento no requiere receta."""
        return "NINGUNA"
```

---

#### Antes (`med_receta_simple.py`):
```python
class MedRecetaSimple(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "RECETA_SIMPLE"
```

#### Después (`med_receta_simple.py`):
```python
class MedRecetaSimple(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "RECETA_SIMPLE"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente que este medicamento requiere receta medica simple."""
        return "RECETA_SIMPLE"
```

---

#### Antes (`med_receta_controlado.py`):
```python
class MedRecetaControlado(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "CONTROLADO"
```

#### Después (`med_receta_controlado.py`):
```python
class MedRecetaControlado(Medicamento):
    @property
    def tipo_medicamento(self) -> str:
        return "CONTROLADO"

    @property
    def tipo_receta_requerida(self) -> str:
        """Define polimorficamente que este medicamento requiere receta controlada con retencion y autorizacion QF."""
        return "RECETA_CONTROLADA"
```

---

### B. Módulo Principal (`main.py` - Menú POS de Ventas)

#### Antes (con anti-patrón `isinstance`):
```python
# CODIGO ANTERIOR:
receta_asociada = None

if isinstance(med_sel, MedRecetaSimple):
    print("\n[REQUISITO SANITARIO] Medicamento sujeto a Receta Medica Simple.")
    folio_r = pedir_texto_no_vacio("   Folio Receta Medica: ")
    medico_r = pedir_texto_no_vacio("   Medico Emisor: ")
    receta_asociada = Receta(numero_folio=folio_r, medico=medico_r)

elif isinstance(med_sel, MedRecetaControlado):
    print("\n[ALERTA SANITARIA] Medicamento CONTROLADO - Requiere receta retenida y autorizada por Quimico Farmaceutico.")
    if recetas_autorizadas:
        ...
```

#### Después (Polimorfismo limpio, CERO `isinstance`):
```python
# CODIGO ACTUALIZADO:
receta_asociada = None

# Despacho polimorfico: cada medicamento define que tipo de receta requiere
tipo_receta = med_sel.tipo_receta_requerida

if tipo_receta == "RECETA_SIMPLE":
    print("\n[REQUISITO SANITARIO] Medicamento sujeto a Receta Medica Simple.")
    folio_r = pedir_texto_no_vacio("   Folio Receta Medica: ")
    medico_r = pedir_texto_no_vacio("   Medico Emisor: ")
    receta_asociada = Receta(numero_folio=folio_r, medico=medico_r)

elif tipo_receta == "RECETA_CONTROLADA":
    print("\n[ALERTA SANITARIA] Medicamento CONTROLADO - Requiere receta retenida y autorizada por Quimico Farmaceutico.")
    if recetas_autorizadas:
        ...
```

---

### C. Capa de Persistencia (`dao/medicamento_dao.py`)

#### Antes:
```python
requiere_ret = 1 if isinstance(med, MedRecetaControlado) and med.requiere_retencion else 0
```

#### Después:
```python
requiere_ret = 1 if med.requiere_retencion else 0
```

---

## 3. Verificación de Cero `isinstance` en el Proyecto

Al ejecutar la búsqueda en todo el código fuente:
```powershell
Get-ChildItem -Path . -Filter "*.py" -Recurse | Select-String -Pattern "\bisinstance\b"
```
**Resultado:** Cero ocurrencias en el código productivo (`main.py`, `model/`, `dao/`, `services/`).

---

## 4. Capturas Reales de Ejecución del Sistema

A continuación se presentan las transcripciones literales y capturas de terminal obtenidas de la ejecución real del sistema en vivo sobre Python 3.14 con la base de datos `farmacia.db`.

### Captura 1: Batería de Pruebas Automatizadas de Polimorfismo (`test_polimorfismo.py`)

```text
================================================================================
  PRUEBA DE POLIMORFISMO: tipo_receta_requerida (SIN isinstance)
================================================================================

ID   | Medicamento                              | Tipo             | Receta Requerida    
------------------------------------------------------------------------------------------
1    | Paracetamol 500mg (16 comprimidos)       | LIBRE            | NINGUNA             
2    | Ibuprofeno 400mg (20 capsulas)           | LIBRE            | NINGUNA             
3    | Tapsin Periodo Noche (6 sobres)          | LIBRE            | NINGUNA             
4    | Aspirina 100mg (VENCIDA TEST)            | LIBRE            | NINGUNA             
5    | Amoxicilina 500mg Jarabe (Importado USD) | RECETA_SIMPLE    | RECETA_SIMPLE       
6    | Loratadina 10mg (30 comprimidos)         | RECETA_SIMPLE    | RECETA_SIMPLE       
7    | Losartan Potasico 50mg (30 comp)         | RECETA_SIMPLE    | RECETA_SIMPLE       
8    | Omeprazol 20mg (28 capsulas)             | RECETA_SIMPLE    | RECETA_SIMPLE       
9    | Clonazepam 2mg (30 comprimidos)          | CONTROLADO       | RECETA_CONTROLADA   
10   | Tramadol 50mg (20 capsulas)              | CONTROLADO       | RECETA_CONTROLADA   
11   | Alprazolam 0.5mg (30 comp)               | CONTROLADO       | RECETA_CONTROLADA   
------------------------------------------------------------------------------------------

================================================================================
  PRUEBA 1: Venta de Medicamento LIBRE (Paracetamol - ID 1)
================================================================================
  Medicamento: Paracetamol 500mg (16 comprimidos)
  tipo_receta_requerida: 'NINGUNA'
  Resultado: VENTA APROBADA (no requiere receta)

================================================================================
  PRUEBA 2: Venta de Medicamento RECETA SIMPLE (Loratadina - ID 6)
================================================================================
  Medicamento: Loratadina 10mg (30 comprimidos)
  tipo_receta_requerida: 'RECETA_SIMPLE'

  2a. Intento SIN receta: BLOQUEADO -> Venta no permitida: El medicamento 'Loratadina 10mg (30 comprimidos)' requiere receta medica simple valida.
  2b. Intento CON receta valida: VENTA APROBADA (receta simple presentada)

================================================================================
  PRUEBA 3: Venta de Medicamento CONTROLADO (Clonazepam - ID 9)
================================================================================
  Medicamento: Clonazepam 2mg (30 comprimidos)
  tipo_receta_requerida: 'RECETA_CONTROLADA'

  3a. Intento SIN receta: BLOQUEADO -> Venta rechazada: 'Clonazepam 2mg (30 comprimidos)' requiere receta medica valida.
  3b. Intento CON receta NO autorizada: BLOQUEADO -> Venta rechazada: El medicamento controlado 'Clonazepam 2mg (30 comprimidos)' requiere autorizacion de un Quimico Farmaceutico.
  3c. Intento CON receta AUTORIZADA por QF: VENTA APROBADA (autorizada por Dra. Maria Gonzalez)

================================================================================
  PRUEBA 4: Medicamento VENCIDO (Aspirina TEST - ID 4)
================================================================================
  Medicamento: Aspirina 100mg (VENCIDA TEST)
  tipo_receta_requerida: 'NINGUNA'
  Fecha vencimiento: 2023-01-01
  esta_vencido(): True
  Intento de venta: BLOQUEADO -> No se puede vender 'Aspirina 100mg (VENCIDA TEST)': se encuentra vencido desde 2023-01-01.

================================================================================
  PRUEBA 5: Despacho polimorfico en logica de main.py (sin isinstance)
================================================================================
  Simulando la logica del menu POS para 3 medicamentos:

  Medicamento: Paracetamol 500mg (16 comprimidos)
    med.tipo_receta_requerida = 'NINGUNA'
    -> Accion: Venta directa, no se solicita receta.

  Medicamento: Loratadina 10mg (30 comprimidos)
    med.tipo_receta_requerida = 'RECETA_SIMPLE'
    -> Accion: Se solicita folio y medico emisor de receta simple.

  Medicamento: Clonazepam 2mg (30 comprimidos)
    med.tipo_receta_requerida = 'RECETA_CONTROLADA'
    -> Accion: Se exige receta retenida + autorizacion del Quimico Farmaceutico.

================================================================================
  TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE
  isinstance eliminado de main.py -> Polimorfismo con tipo_receta_requerida
================================================================================
```

---

### Captura 2: Terminal POS interactiva (`main.py` - Menú 1)

Demostración del flujo de compras en vivo con validaciones polimórficas:

#### Paso 1: Venta Libre (Paracetamol ID 1) — No solicita receta
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 1
 Cantidad de 'Paracetamol 500mg (16 comprimidos)': 2
[OK] 2 unidad(es) de 'Paracetamol 500mg (16 comprimidos)' agregadas ($1,890 CLP/u).
```

#### Paso 2: Receta Simple (Loratadina ID 6) — Despacho polimórfico solicita Folio y Médico
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 6
 Cantidad de 'Loratadina 10mg (30 comprimidos)': 1

[REQUISITO SANITARIO] Medicamento sujeto a Receta Medica Simple.
   Folio Receta Medica: FOLIO-RS-2026
   Medico Emisor: Dra. Camila Vergara
[OK] 1 unidad(es) de 'Loratadina 10mg (30 comprimidos)' agregadas ($4,890 CLP/u).
```

#### Paso 3: Producto Vencido (Aspirina ID 4) — Bloqueo de seguridad sanitaria
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 4
 Cantidad de 'Aspirina 100mg (VENCIDA TEST)': 1

[OPERACION DENEGADA POR SEGURIDAD SANITARIA]: No se puede vender 'Aspirina 100mg (VENCIDA TEST)': se encuentra vencido desde 2023-01-01.
```

#### Paso 4: Medicamento Controlado (Clonazepam ID 9) — Bloqueo sin autorización QF
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 9
 Cantidad de 'Clonazepam 2mg (30 comprimidos)': 1

[ALERTA SANITARIA] Medicamento CONTROLADO - Requiere receta retenida y autorizada por Quimico Farmaceutico.
   Folio Receta Retenida: FOLIO-RC-NO-AUTH

[OPERACION DENEGADA POR SEGURIDAD SANITARIA]: Venta rechazada: El medicamento controlado 'Clonazepam 2mg (30 comprimidos)' requiere autorizacion de un Quimico Farmaceutico.
```

#### Paso 5: Emisión de Boleta Electrónica de la Venta Nro. 1
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 0

[EXITO] Venta registrada exitosamente en base de datos con Nro: 1.

======================================================================
                   FARMACIA CRUZ DEL SUR S.A.
             R.U.T.: 76.543.210-K - GIRO: FARMACIA
           Av. Concha y Toro 1340, Puente Alto, Santiago
======================================================================
 BOLETA ELECTRONICA DE VENTA Nro. 1
 Fecha Emision : 2026-10-13 02:18:29
 Cliente        : Pedro Tapia
 RUT Cliente    : 18.123.456-3
 Atendido Por   : Juan Perez
----------------------------------------------------------------------
 CANT  | DESCRIPCION                          |     P.UNIT |   SUBTOTAL
----------------------------------------------------------------------
 2     | Paracetamol 500mg (16 comprimidos)   | $    1,890 | $    3,780
 1     | Loratadina 10mg (30 comprimidos)     | $    4,890 | $    4,890
----------------------------------------------------------------------
 NETO (19% IVA incluido) : $                                      7,286 CLP
 IVA (19%)               : $                                      1,384 CLP
 TOTAL A PAGAR           : $                                      8,670 CLP
======================================================================
           Gracias por su compra en Farmacia Cruz del Sur
     Timbre Electronico SII - Res. Nro. 80 del 2026 - Verifique en sii.cl
======================================================================
```

---

### Captura 3: Módulo Sanitario QF (Menú 5) y Venta Autorizada de Controlado

#### Paso 1: Autorización Profesional de Receta por el Químico Farmacéutico
```text
========================================================================================
  MODULO SANITARIO: AUTORIZACION Y RETENCION DE RECETAS (QF)
========================================================================================
 Quimico Farmaceutico Titular: Dra. Maria Gonzalez (Registro Sanitario: QF-88421)

 Ingrese numero de folio de la receta medica: FOLIO-CTRL-9921
 Ingrese nombre completo del medico emisor: Dr. Rodrigo Morales

[EXITO] Receta Folio 'FOLIO-CTRL-9921' AUTORIZADA y RETENIDA exitosamente en el sistema.
```

#### Paso 2: Venta en POS seleccionando la receta previamente autorizada
```text
Ingrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):
 ID Medicamento: 9
 Cantidad de 'Clonazepam 2mg (30 comprimidos)': 2

[ALERTA SANITARIA] Medicamento CONTROLADO - Requiere receta retenida y autorizada por Quimico Farmaceutico.
   Recetas autorizadas disponibles en sesion:
     1. Folio: FOLIO-CTRL-9921 | Dr(a). Dr. Rodrigo Morales
     0. Ingresar otra receta no autorizada (Prueba de Bloqueo)
   Seleccione opcion de receta: 1
[OK] 2 unidad(es) de 'Clonazepam 2mg (30 comprimidos)' agregadas ($9,990 CLP/u).
```

#### Paso 3: Emisión de Boleta Electrónica de la Venta Nro. 2 (Controlado Exitoso)
```text
[EXITO] Venta registrada exitosamente en base de datos con Nro: 2.

======================================================================
                   FARMACIA CRUZ DEL SUR S.A.
             R.U.T.: 76.543.210-K - GIRO: FARMACIA
           Av. Concha y Toro 1340, Puente Alto, Santiago
======================================================================
 BOLETA ELECTRONICA DE VENTA Nro. 2
 Fecha Emision : 2026-10-13 02:18:33
 Cliente        : Pedro Tapia
 RUT Cliente    : 18.123.456-3
 Atendido Por   : Juan Perez
----------------------------------------------------------------------
 CANT  | DESCRIPCION                          |     P.UNIT |   SUBTOTAL
----------------------------------------------------------------------
 2     | Clonazepam 2mg (30 comprimidos)      | $    9,990 | $   19,980
----------------------------------------------------------------------
 NETO (19% IVA incluido) : $                                     16,790 CLP
 IVA (19%)               : $                                      3,190 CLP
 TOTAL A PAGAR           : $                                     19,980 CLP
======================================================================
           Gracias por su compra en Farmacia Cruz del Sur
     Timbre Electronico SII - Res. Nro. 80 del 2026 - Verifique en sii.cl
======================================================================
```

---

### Captura 4: Trazabilidad y Bitácora de Auditoría SQLite (Menú 7)

Demostración de cómo todos los eventos de seguridad sanitaria (bloqueos, autorizaciones y persistencia) quedan registrados de forma inmutable:

```text
========================================================================================
  BITACORA DE AUDITORIA Y EVENTOS DE SEGURIDAD (SQLITE)
========================================================================================
 ID   | Fecha y Hora        | Tipo Evento                | Usuario          | Detalle
---------------------------------------------------------------------------------------------------------
 14   | 2026-10-13 02:18:34 | API_DOLAR_EXITO            | Sistema          | Cotizacion oficial USD obtenida exitosamente: $978.61 CLP.
 13   | 2026-10-13 02:18:33 | VENTA_REGISTRADA_BD        | Juan Perez       | Venta ID 2 persistida por total de $19,980 CLP. Cliente: 18.123.456-3
 10   | 2026-10-13 02:18:31 | RECETA_AUTORIZADA          | Dra. Maria Gonza | Receta Folio 'FOLIO-CTRL-9921' autorizada y retenida por QF Dra. Maria Gonzalez.
 6    | 2026-10-13 02:18:29 | VENTA_REGISTRADA_BD        | Juan Perez       | Venta ID 1 persistida por total de $8,670 CLP. Cliente: 18.123.456-3
 5    | 2026-10-13 02:18:29 | SEGURIDAD_VENTA_DENEGADA   | Juan Perez       | Venta rechazada: El medicamento controlado 'Clonazepam 2mg (30 comprimidos)' requiere autorizacion de un Quimico Farmaceutico.
 4    | 2026-10-13 02:18:29 | SEGURIDAD_VENTA_DENEGADA   | Juan Perez       | No se puede vender 'Aspirina 100mg (VENCIDA TEST)': se encuentra vencido desde 2023-01-01.
 1    | 2026-10-13 02:18:27 | SISTEMA_INIT               | Sistema          | Sistema Farmacia Cruz del Sur S.A. iniciado con persistencia SQLite y conexion segura a API.
---------------------------------------------------------------------------------------------------------
```

---

## 5. Conclusión
El requerimiento fue resuelto aplicando rigurosamente los principios de **Programación Orientada a Objetos**:
- Se erradicó el uso de `isinstance` tanto de `main.py` como de `medicamento_dao.py`.
- Se implementó la propiedad polimórfica `tipo_receta_requerida` y `requiere_retencion`.
- El sistema mantiene el 100% de sus funcionalidades, robustez de seguridad sanitaria y persistencia transaccional ACID en SQLite.
