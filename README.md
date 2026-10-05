# Farmacia Cruz del Sur S.A. - Sistema POS & Gestor Sanitario

Sistema integral de gestión de farmacia, control de inventario, terminal de ventas (POS) y validación de medicamentos con integración en tiempo real a servicios financieros y sanitarios.

## Características Principales

- **Terminal POS de Ventas**: Registro de compras en tiempo real, selección de cliente/vendedor y cálculo automatizado.
- **Emisión de Boletas Electrónicas**: Boleta oficial con desglose de Subtotal Neto, IVA (19%) y timbre electrónico tributario.
- **Cotización USD en Tiempo Real**: Sincronización automática con `mindicador.cl` (Banco Central de Chile) para la conversión de precios en medicamentos importados.
- **Red Nacional de Farmacias de Turno**: Integración con el servicio en vivo del Ministerio de Salud de Chile (MINSAL) con filtro por comuna.
- **Módulo Sanitario de Recetas Controladas**: Verificación y retención de recetas de medicamentos controlados autorizadas por el Químico Farmacéutico Titular.
- **Bitácora de Auditoría & Seguridad**: Registro centralizado de transacciones, aperturas de sesión e historial de eventos del sistema.

## Estructura del Proyecto

```text
farmacia_ev2/
── main.py                     # Punto de entrada principal y menú interactivo
── model/                      # Modelo de dominio y POO Seguro
│   ── cliente.py              # Entidad Cliente
│   ── vendedor.py             # Entidad Vendedor (Cajero)
│   ── quimico_farmaceutico.py # Entidad QF Titular
│   ── medicamento.py          # Clase base de Medicamentos
│   ── med_sin_receta.py       # Subtipo Venta Libre
│   ── med_receta_simple.py    # Subtipo Venta con Receta Simple
│   ── med_receta_controlado.py# Subtipo Receta Retenida
│   ── receta.py               # Entidad Receta Médica
│   ── venta.py                # Modelo de Venta y Carro
│   ── detalle_venta.py        # Detalle de ítem vendido
│   ── excepciones.py          # Excepciones de negocio personalizadas
── services/                   # Capa de Servicios de Negocio e Integración
    ── api_service.py          # Sincronización en tiempo real (Mindicador & MINSAL)
    ── inventario_service.py   # Gestión de catálogo y stock
    ── venta_service.py        # Proceso de venta y generación de boleta fiscal
    ── auditoria_service.py    # Registro de auditoría y seguridad
```