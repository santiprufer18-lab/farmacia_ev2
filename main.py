import sys
from model.cliente import Cliente
from model.vendedor import Vendedor
from model.quimico_farmaceutico import QuimicoFarmaceutico
from model.receta import Receta
from model.med_sin_receta import MedSinReceta
from model.med_receta_simple import MedRecetaSimple
from model.med_receta_controlado import MedRecetaControlado
from model.venta import Venta
from model.excepciones import MedicamentoVencidoException, RecetaInvalidaException, VentaNoAutorizadaException

from services.api_service import APIService
from services.inventario_service import InventarioService
from services.venta_service import VentaService
from services.auditoria_service import AuditoriaService


def imprimir_encabezado(titulo: str):
    print("\n" + "=" * 84)
    print(f"  {titulo.upper()}")
    print("=" * 84)


def cargar_datos_iniciales():
    """Inicializa los servicios del sistema, personal y clientes base."""
    inventario_service = InventarioService()
    venta_service = VentaService()

    vendedores = [
        Vendedor(rut="19.876.543-2", nombre="Juan Pérez", caja_asignada=1),
        Vendedor(rut="18.999.888-7", nombre="Camila Torres", caja_asignada=2)
    ]
    quimicos = [
        QuimicoFarmaceutico(rut="15.432.109-8", nombre="Dra. María González", num_registro="QF-88421")
    ]
    clientes = [
        Cliente(rut="18.123.456-7", nombre="Pedro Tapia"),
        Cliente(rut="12.345.678-9", nombre="Andrea Silva")
    ]

    AuditoriaService.registrar_evento(
        tipo="SISTEMA_INIT",
        detalle="Sistema de Farmacia Cruz del Sur iniciado correctamente"
    )

    return inventario_service, venta_service, vendedores, quimicos, clientes


def mostrar_resumen_catalogo(catalogo: list, valor_dolar: float):
    print(f"\n Cotización USD Oficial (Banco Central / mindicador.cl): $1 USD = ${valor_dolar:,.2f} CLP")
    print(f" {'ID':<3} | {'Medicamento':<36} | {'Tipo':<20} | {'Stock':<5} | {'Precio Final / Moneda de Origen':>26}")
    print("-" * 100)
    for i, med in enumerate(catalogo, start=1):
        precio_clp = med.get_precio_final(valor_dolar)
        vencido = " [VENCIDO]" if med.esta_vencido() else ""
        nombre_display = (med.nombre + vencido)[:36]

        if med.es_importado:
            precio_fmt = f"${precio_clp:>7,.0f} CLP (${med.precio_base:,.2f} USD)"
        else:
            precio_fmt = f"${precio_clp:>7,.0f} CLP"

        print(f" {i:<3} | {nombre_display:<36} | {med.__class__.__name__:<20} | {med.stock:<5} | {precio_fmt:>26}")
    print("-" * 100)


def menu_pos_venta(inventario_service: InventarioService, venta_service: VentaService, vendedores: list, quimicos: list, clientes: list, recetas_autorizadas: list):
    imprimir_encabezado("TERMINAL POS - REGISTRO DE VENTA Y FACTURACIÓN")

    # Obtenemos dólar en tiempo real
    print(" Sincronizando tipo de cambio oficial del Dólar USD en tiempo real...")
    valor_dolar = APIService.obtener_dolar_tiempo_real()
    print(f" Valor del Dólar USD en Chile Hoy: ${valor_dolar:,.2f} CLP\n")

    # Selección de Vendedor
    print("Seleccione el vendedor a cargo de la caja:")
    for idx, v in enumerate(vendedores, 1):
        print(f"  {idx}. {v.nombre} (Caja {v.caja_asignada})")
    try:
        opt_v = int(input(" Opción: ")) - 1
        if opt_v < 0:
            raise IndexError()
        vendedor_sel = vendedores[opt_v]
    except (ValueError, IndexError):
        print(" Selección de vendedor inválida.")
        return

    # Selección o registro de cliente
    print("\nSeleccione o ingrese el cliente:")
    for idx, c in enumerate(clientes, 1):
        print(f"  {idx}. {c.nombre} (RUT: {c.rut})")
    print(f"  {len(clientes) + 1}. [ + ] Registrar nuevo cliente")
    try:
        opt_c = int(input(" Opción: ")) - 1
        if opt_c < 0:
            raise IndexError()
        if opt_c == len(clientes):
            rut_c = input("   RUT Cliente: ").strip()
            nom_c = input("   Nombre completo: ").strip()
            if not rut_c or not nom_c:
                print(" Datos requeridos.")
                return
            cliente_sel = Cliente(rut=rut_c, nombre=nom_c)
            clientes.append(cliente_sel)
        else:
            cliente_sel = clientes[opt_c]
    except (ValueError, IndexError):
        print(" Selección de cliente inválida.")
        return

    venta = Venta(cliente=cliente_sel, vendedor=vendedor_sel)
    print(f"\n Sesión de Venta aperturada para: {cliente_sel.nombre} (RUT: {cliente_sel.rut})")

    catalogo = inventario_service.listar_todos()

    while True:
        mostrar_resumen_catalogo(catalogo, valor_dolar)
        print("\n Ingrese el ID del medicamento a agregar (o marque '0' para finalizar el carro):")
        try:
            opcion_str = input(" ID Producto: ").strip()
            if opcion_str == "0":
                break

            idx_med = int(opcion_str) - 1
            med_sel = inventario_service.obtener_por_id(idx_med)
            if not med_sel:
                print(" Código de producto no encontrado.")
                continue

            cant = int(input(f" Cantidad de '{med_sel.nombre}': "))
            if cant <= 0:
                print(" La cantidad debe ser mayor a 0.")
                continue

            receta_asociada = None

            if isinstance(med_sel, MedRecetaSimple):
                print(" Medicamento sujeto a Receta Médica Simple.")
                folio_r = input("   Folio Receta Médica: ").strip()
                medico_r = input("   Médico Emisor: ").strip()
                if not folio_r or not medico_r:
                    print(" Folio y médico son requeridos.")
                    continue
                receta_asociada = Receta(numero_folio=folio_r, medico=medico_r)

            elif isinstance(med_sel, MedRecetaControlado):
                print(" Medicamento CONTROLADO - Requiere receta retenida y autorizada por Químico Farmacéutico.")
                if recetas_autorizadas:
                    print("   Recetas Autorizadas en Sistema:")
                    for idx_r, r in enumerate(recetas_autorizadas, 1):
                        print(f"     {idx_r}. Folio: {r.numero_folio} | Dr(a). {r.medico}")
                    print("     0. Ingresar receta no autorizada (Prueba de Bloqueo)")
                    opt_r = input("   Seleccione receta a aplicar: ").strip()
                    if opt_r.isdigit() and 0 < int(opt_r) <= len(recetas_autorizadas):
                        receta_asociada = recetas_autorizadas.pop(int(opt_r) - 1)
                    else:
                        folio_r = input("   Folio Receta: ").strip()
                        receta_asociada = Receta(numero_folio=folio_r, medico="Dr. No Verificado", retenida=True)
                else:
                    folio_r = input("   Folio Receta Retenida: ").strip()
                    receta_asociada = Receta(numero_folio=folio_r, medico="Dr. No Verificado", retenida=True)

            venta.agregar_detalle(medicamento=med_sel, cantidad=cant, receta=receta_asociada, valor_dolar=valor_dolar)
            
            p_unit = med_sel.get_precio_final(valor_dolar)
            if med_sel.es_importado:
                print(f" {cant} unidad(es) de '{med_sel.nombre}' agregadas (Precio Importado: ${med_sel.precio_base} USD x ${valor_dolar:,.2f} = ${p_unit:,.0f} CLP/u).")
            else:
                print(f" {cant} unidad(es) de '{med_sel.nombre}' agregadas (${p_unit:,.0f} CLP/u).")

        except (MedicamentoVencidoException, RecetaInvalidaException, VentaNoAutorizadaException) as e_negocio:
            print(f"\n [OPERACIÓN DENEGADA POR SEGURIDAD]: {e_negocio}")
        except ValueError as e_val:
            print(f"\n [ENTRADA INVÁLIDA]: {e_val}")

    if not venta.detalles:
        print("\n No se agregaron productos. Venta cancelada.")
        return

    # Registrar la venta en el servicio
    if venta_service.registrar_venta(venta):
        boleta_fmt = VentaService.generar_boleta_texto(venta, valor_dolar)
        print("\n" + boleta_fmt)


def menu_inventario(inventario_service: InventarioService):
    imprimir_encabezado("GESTIÓN DE INVENTARIO Y CATÁLOGO DE MEDICAMENTOS")
    valor_dolar = APIService.obtener_dolar_tiempo_real()
    print(f" Cotización USD Oficial Actualizada: ${valor_dolar:,.2f} CLP\n")

    print(" 1. Ver Catálogo Completo (Precios CLP y Dólar Importaciones)")
    print(" 2. Buscar Medicamento por Nombre")
    print(" 3. Ver Medicamentos Vencidos o Próximos a Vencer")
    opc = input("\n Seleccione opción [1-3]: ").strip()

    if opc == "1":
        mostrar_resumen_catalogo(inventario_service.listar_todos(), valor_dolar)
    elif opc == "2":
        nombre = input(" Ingrese nombre o componente a buscar: ").strip()
        resultados = inventario_service.buscar_por_nombre(nombre)
        if resultados:
            mostrar_resumen_catalogo(resultados, valor_dolar)
        else:
            print(f" No se encontraron productos que coincidan con '{nombre}'.")
    elif opc == "3":
        vencidos = inventario_service.obtener_vencidos()
        if vencidos:
            print(f"\n ATENCIÓN: Se encontraron {len(vencidos)} medicamentos VENCIDOS en stock:")
            mostrar_resumen_catalogo(vencidos, valor_dolar)
        else:
            print("\n No hay medicamentos vencidos en el inventario activo.")


def menu_farmacias_minsal():
    imprimir_encabezado("RED NACIONAL DE FARMACIAS DE TURNO - MINISTERIO DE SALUD")
    print(" Consultando Red de Servicios del Ministerio de Salud (MINSAL) en tiempo real...\n")

    comuna = input(" Ingrese comuna a consultar (ej: Puente Alto, Santiago, Providencia) o presione ENTER para ver todas: ").strip()
    locales = APIService.obtener_farmacias_turno(comuna_filtro=comuna if comuna else None)

    if not locales:
        print(f" No se registraron farmacias de turno activas para la comuna '{comuna}'.")
        return

    print(f"\n Farmacias de Turno Registradas en MINSAL ({len(locales)} locales obtenidos):")
    print(f" {'Comuna':<16} | {'Nombre Local':<30} | {'Dirección':<28} | {'Horario':<15}")
    print("-" * 96)
    for f in locales[:25]:
        print(f" {f['comuna'][:16]:<16} | {f['nombre'][:30]:<30} | {f['direccion'][:28]:<28} | {f['horario']:<15}")
    print("-" * 96)


def menu_autorizar_receta(quimicos: list, recetas_autorizadas: list):
    imprimir_encabezado("MÓDULO PROFESIONAL DE AUTORIZACION Y RETENCION DE RECETAS")
    if not quimicos:
        print(" No hay Químico Farmacéutico disponible.")
        return

    qf = quimicos[0]
    print(f" Químico Farmacéutico Titular: {qf.nombre} (Registro Sanitario: {qf.num_registro})\n")

    folio = input(" Ingrese número de folio de la receta médica: ").strip()
    medico = input(" Ingrese nombre del médico emisor: ").strip()

    if not folio or not medico:
        print("Folio y médico son datos obligatorios.")
        return

    receta = Receta(numero_folio=folio, medico=medico, retenida=True)
    qf.autorizar_controlado(receta)
    recetas_autorizadas.append(receta)

    AuditoriaService.registrar_evento(
        tipo="RECETA_AUTORIZADA",
        detalle=f"Receta Folio '{folio}' autorizada y retenida por QF {qf.nombre}",
        usuario=qf.nombre
    )
    print(f"\n Receta Folio '{folio}' AUTORIZADA y RETENIDA exitosamente en el sistema.")


def menu_historial_ventas(venta_service: VentaService):
    imprimir_encabezado("HISTORIAL DE VENTAS Y REEMISION DE BOLETAS")
    ventas = venta_service.listar_ventas()

    if not ventas:
        print("No se han registrado ventas durante esta sesion.")
        return

    print(f" {'N°':<3} | {'Fecha':<20} | {'Cliente':<25} | {'Vendedor':<20} | {'Total CLP':>12}")
    print("-" * 88)
    for idx, v in enumerate(ventas, 1):
        print(f" {idx:<3} | {v.fecha:<20} | {v.cliente.nombre[:25]:<25} | {v.vendedor.nombre[:20]:<20} | ${v.total:>11,.0f}")
    print("-" * 88)

    opt = input("\n Ingrese el N° de venta para reimprimir Boleta (o press ENTER para regresar): ").strip()
    if opt.isdigit() and 0 < int(opt) <= len(ventas):
        venta_sel = ventas[int(opt) - 1]
        valor_dolar = APIService.obtener_dolar_tiempo_real()
        print("\n" + VentaService.generar_boleta_texto(venta_sel, valor_dolar))


def menu_auditoria():
    imprimir_encabezado("REGISTRO DE AUDITORIA Y EVENTOS DE SEGURIDAD")
    eventos = AuditoriaService.obtener_historial()

    if not eventos:
        print("No hay eventos registrados en la bitocora de auditoria.")
        return

    print(f" {'Fecha y Hora':<19} | {'Tipo Evento':<20} | {'Usuario':<15} | {'Detalle Evento'}")
    print("-" * 96)
    for ev in eventos:
        print(f" {ev['fecha']:<19} | {ev['tipo']:<20} | {ev['usuario']:<15} | {ev['detalle']}")
    print("-" * 96)


def main():
    inventario_service, venta_service, vendedores, quimicos, clientes = cargar_datos_iniciales()
    recetas_autorizadas = []

    while True:
        valor_dolar_actual = APIService.obtener_dolar_tiempo_real()

        imprimir_encabezado("FARMACIA CRUZ DEL SUR S.A. - SISTEMA POS Y GESTIÓN SANITARIA")
        print(f"  Cotización USD Oficial (Banco Central / mindicador.cl): ${valor_dolar_actual:,.2f} CLP")
        print("  ----------------------------------------------------------------------------")
        print("  1. Registrar Nueva Venta (Terminal POS)")
        print("  2. Consultar Catalogo de Medicamentos e Inventario (Precio CLP / USD)")
        print("  3. Red Nacional de Farmacias de Turno (MINSAL)")
        print("  4. Modulo de Autorizacion de Recetas Controladas (QF)")
        print("  5. Historial de Ventas y Reemision de Boletas SII")
        print("  6. Bitacora de Auditoria y Seguridad del Sistema")
        print("  0. Salir del Sistema")
        print("-" * 84)

        opcion = input(" Seleccione opcion [0-6]: ").strip()

        if opcion == "1":
            menu_pos_venta(inventario_service, venta_service, vendedores, quimicos, clientes, recetas_autorizadas)
        elif opcion == "2":
            menu_inventario(inventario_service)
        elif opcion == "3":
            menu_farmacias_minsal()
        elif opcion == "4":
            menu_autorizar_receta(quimicos, recetas_autorizadas)
        elif opcion == "5":
            menu_historial_ventas(venta_service)
        elif opcion == "6":
            menu_auditoria()
        elif opcion == "0":
            print("\n Cerrando sesión en Sistema Farmacia Cruz del Sur S.A. ¡Hasta pronto!")
            sys.exit(0)
        else:
            print("Opción inválida. Seleccione un número entre 0 y 6.")

        input("\n Presione ENTER para volver al menú principal...")


if __name__ == "__main__":
    main()
