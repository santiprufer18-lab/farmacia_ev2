import sys
from datetime import datetime
from dao.database import inicializar_bd
from dao.medicamento_dao import MedicamentoDAO
from dao.cliente_dao import ClienteDAO
from dao.venta_dao import VentaDAO
from dao.personal_dao import PersonalDAO
from model.cliente import Cliente
from model.med_sin_receta import MedSinReceta
from model.med_receta_simple import MedRecetaSimple
from model.med_receta_controlado import MedRecetaControlado
from model.receta import Receta
from model.venta import Venta
from model.excepciones import (
    MedicamentoVencidoException,
    RecetaInvalidaException,
    VentaNoAutorizadaException
)
from services.api_service import APIService
from services.auditoria_service import AuditoriaService


# ==============================================================================
# FUNCIONES AUXILIARES DE VALIDACION DE ENTRADAS (TIPO, FORMATO Y RANGO)
# ==============================================================================

def validar_rut_chileno(rut_str: str) -> bool:
    """Valida tipo, formato y algoritmo modulo 11 del RUT chileno."""
    if not rut_str:
        return False
    limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(limpio) < 8 or len(limpio) > 9:
        return False
    cuerpo = limpio[:-1]
    dv = limpio[-1]
    if not cuerpo.isdigit() or (not dv.isdigit() and dv != "K"):
        return False

    suma = 0
    multiplicador = 2
    for d in reversed(cuerpo):
        suma += int(d) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    dv_esperado = "K" if resto == 10 else ("0" if resto == 11 else str(resto))
    return dv == dv_esperado


def pedir_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    """Valida que la entrada sea de tipo entero y cumpla el rango establecido."""
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"[ERROR DE ENTRADA] El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"[ERROR DE ENTRADA] El valor debe ser menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("[ERROR DE ENTRADA] Ingrese un numero entero valido.")


def pedir_flotante(mensaje: str, minimo: float = None) -> float:
    """Valida que la entrada sea de tipo decimal y cumpla el rango minimo."""
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(entrada)
            if minimo is not None and valor < minimo:
                print(f"[ERROR DE ENTRADA] El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("[ERROR DE ENTRADA] Ingrese un numero decimal valido.")


def pedir_texto_no_vacio(mensaje: str, min_longitud: int = 1) -> str:
    """Valida que el texto no este vacio y cumpla con una longitud minima."""
    while True:
        texto = input(mensaje).strip()
        if len(texto) < min_longitud:
            print(f"[ERROR DE ENTRADA] El texto debe tener al menos {min_longitud} caracteres.")
            continue
        return texto


def pedir_fecha_vencimiento(mensaje: str) -> str:
    """Valida que la entrada tenga el formato AAAA-MM-DD y sea una fecha existente en el calendario."""
    while True:
        fecha_str = input(mensaje).strip()
        try:
            datetime.strptime(fecha_str, "%Y-%m-%d")
            return fecha_str
        except ValueError:
            print("[ERROR DE ENTRADA] Formato de fecha invalido. Debe usar AAAA-MM-DD (ejemplo: 2027-12-31).")


def pedir_rut_valido(mensaje: str) -> str:
    """Valida el ingreso de un RUT chileno en tipo, formato y digito verificador."""
    while True:
        rut_str = input(mensaje).strip()
        if validar_rut_chileno(rut_str):
            limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
            cuerpo = limpio[:-1]
            dv = limpio[-1]
            cuerpo_fmt = f"{int(cuerpo):,}".replace(",", ".")
            return f"{cuerpo_fmt}-{dv}"
        print("[ERROR DE ENTRADA] RUT invalido. Debe incluir digitos validos y digito verificador correcto.")


# ==============================================================================
# PRESENTACION Y CATALOGO
# ==============================================================================

def imprimir_encabezado(titulo: str):
    print("\n" + "=" * 88)
    print(f"  {titulo.upper()}")
    print("=" * 88)


def mostrar_resumen_catalogo(catalogo: list, valor_dolar: float):
    print(f"\n Cotizacion USD Oficial (mindicador.cl): $1 USD = ${valor_dolar:,.2f} CLP")
    print(f" {'ID':<4} | {'Medicamento':<36} | {'Tipo':<16} | {'Stock':<6} | {'Precio Final / Moneda Origen':>28}")
    print("-" * 102)
    for med in catalogo:
        precio_clp = med.get_precio_final(valor_dolar)
        vencido = " [VENCIDO]" if med.esta_vencido() else ""
        nombre_disp = (med.nombre + vencido)[:36]
        if med.es_importado:
            precio_fmt = f"${precio_clp:>8,.0f} CLP (${med.precio_base:,.2f} USD)"
        else:
            precio_fmt = f"${precio_clp:>8,.0f} CLP"

        tipo_display = med.tipo_medicamento
        id_str = str(med.id_medicamento) if med.id_medicamento else "-"
        print(f" {id_str:<4} | {nombre_disp:<36} | {tipo_display:<16} | {med.stock:<6} | {precio_fmt:>28}")
    print("-" * 102)


def generar_boleta_texto(venta: Venta, valor_dolar: float) -> str:
    """Genera la representacion en texto formal de la boleta electronica."""
    subtotal_neto = venta.total / 1.19
    iva = venta.total - subtotal_neto
    lineas = []
    lineas.append("=" * 70)
    lineas.append("                   FARMACIA CRUZ DEL SUR S.A.")
    lineas.append("             R.U.T.: 76.543.210-K - GIRO: FARMACIA")
    lineas.append("           Av. Concha y Toro 1340, Puente Alto, Santiago")
    lineas.append("=" * 70)
    lineas.append(f" BOLETA ELECTRONICA DE VENTA Nro. {venta.id_venta or 'PENDIENTE'}")
    lineas.append(f" Fecha Emision : {venta.fecha}")
    lineas.append(f" Cliente        : {venta.cliente.nombre}")
    lineas.append(f" RUT Cliente    : {venta.cliente.rut}")
    lineas.append(f" Atendido Por   : {venta.vendedor.nombre}")
    lineas.append("-" * 70)
    lineas.append(f" {'CANT':<5} | {'DESCRIPCION':<36} | {'P.UNIT':>10} | {'SUBTOTAL':>10}")
    lineas.append("-" * 70)

    for det in venta.detalles:
        p_u = det.precio_unitario
        lineas.append(f" {det.cantidad:<5} | {det.medicamento.nombre[:36]:<36} | ${p_u:>9,.0f} | ${det.subtotal:>9,.0f}")

    lineas.append("-" * 70)
    lineas.append(f" NETO (19% IVA incluido) : ${subtotal_neto:>43,.0f} CLP")
    lineas.append(f" IVA (19%)               : ${iva:>43,.0f} CLP")
    lineas.append(f" TOTAL A PAGAR           : ${venta.total:>43,.0f} CLP")
    lineas.append("=" * 70)
    lineas.append("           Gracias por su compra en Farmacia Cruz del Sur")
    lineas.append("     Timbre Electronico SII - Res. Nro. 80 del 2026 - Verifique en sii.cl")
    lineas.append("=" * 70)
    return "\n".join(lineas)


# ==============================================================================
# MENU 1: TERMINAL POS (REGISTRO TRANSACCIONAL DE VENTA Y DETALLES)
# ==============================================================================

def menu_pos_venta(recetas_autorizadas: list):
    imprimir_encabezado("TERMINAL POS - REGISTRO DE VENTA Y FACTURACION")

    print("[SISTEMA] Consultando tipo de cambio del Dolar USD en tiempo real...")
    valor_dolar = APIService.obtener_dolar_tiempo_real()
    print(f"[COTIZACION] Valor del Dolar aplicado: ${valor_dolar:,.2f} CLP\n")

    # 1. Seleccion de vendedor
    vendedores = PersonalDAO.listar_vendedores()
    if not vendedores:
        print("[ERROR] No hay vendedores registrados en la base de datos.")
        return

    print("Seleccione el vendedor a cargo:")
    for idx, v in enumerate(vendedores, 1):
        print(f"  {idx}. {v.nombre} (Caja {v.caja_asignada})")
    opt_v = pedir_entero(" Opcion: ", minimo=1, maximo=len(vendedores))
    vendedor_sel = vendedores[opt_v - 1]

    # 2. Seleccion o creacion de cliente
    clientes = ClienteDAO.listar_todos()
    print("\nSeleccione o ingrese el cliente:")
    for idx, c in enumerate(clientes, 1):
        print(f"  {idx}. {c.nombre} (RUT: {c.rut})")
    print(f"  {len(clientes) + 1}. [ + ] Registrar nuevo cliente")
    opt_c = pedir_entero(" Opcion: ", minimo=1, maximo=len(clientes) + 1)

    if opt_c == len(clientes) + 1:
        print("\n--- Registro de Nuevo Cliente ---")
        rut_c = pedir_rut_valido("   RUT Cliente: ")
        nom_c = pedir_texto_no_vacio("   Nombre completo: ", min_longitud=3)
        try:
            cliente_sel = Cliente(rut=rut_c, nombre=nom_c)
            ClienteDAO.crear(cliente_sel)
            print(f"[EXITO] Cliente '{cliente_sel.nombre}' registrado con ID {cliente_sel.id_cliente}.")
        except Exception as err:
            print(f"[ERROR] No se pudo guardar cliente: {err}")
            return
    else:
        cliente_sel = clientes[opt_c - 1]

    # 3. Apertura de la sesion de venta (Objeto Venta)
    venta = Venta(cliente=cliente_sel, vendedor=vendedor_sel)
    print(f"\nSesion de venta aperturada para: {cliente_sel.nombre} (RUT: {cliente_sel.rut})")

    # 4. Seleccion interactiva de medicamentos
    while True:
        catalogo = MedicamentoDAO.listar_todos()
        mostrar_resumen_catalogo(catalogo, valor_dolar)
        print("\nIngrese el ID del medicamento a agregar al carrito (o marque '0' para finalizar el carro):")
        id_med_in = pedir_entero(" ID Medicamento: ", minimo=0)
        if id_med_in == 0:
            break

        med_sel = MedicamentoDAO.obtener_por_id(id_med_in)
        if not med_sel:
            print(f"[ERROR] No existe medicamento con ID {id_med_in}.")
            continue

        cant = pedir_entero(f" Cantidad de '{med_sel.nombre}': ", minimo=1)

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
                print("   Recetas autorizadas disponibles en sesion:")
                for idx_r, r in enumerate(recetas_autorizadas, 1):
                    print(f"     {idx_r}. Folio: {r.numero_folio} | Dr(a). {r.medico}")
                print("     0. Ingresar otra receta no autorizada (Prueba de Bloqueo)")
                opt_r = pedir_entero("   Seleccione opcion de receta: ", minimo=0, maximo=len(recetas_autorizadas))
                if opt_r > 0:
                    receta_asociada = recetas_autorizadas.pop(opt_r - 1)
                else:
                    folio_r = pedir_texto_no_vacio("   Folio Receta: ")
                    receta_asociada = Receta(numero_folio=folio_r, medico="Dr. No Verificado", retenida=True)
            else:
                folio_r = pedir_texto_no_vacio("   Folio Receta Retenida: ")
                receta_asociada = Receta(numero_folio=folio_r, medico="Dr. No Verificado", retenida=True)

        try:
            # Agrega el detalle aplicando polimorfismo y reglas de negocio
            venta.agregar_detalle(medicamento=med_sel, cantidad=cant, receta=receta_asociada, valor_dolar=valor_dolar)
            p_unit = med_sel.get_precio_final(valor_dolar)
            if med_sel.es_importado:
                print(f"[OK] {cant} unidad(es) de '{med_sel.nombre}' agregadas (Precio Importado: ${med_sel.precio_base:,.2f} USD x ${valor_dolar:,.2f} = ${p_unit:,.0f} CLP/u).")
            else:
                print(f"[OK] {cant} unidad(es) de '{med_sel.nombre}' agregadas (${p_unit:,.0f} CLP/u).")

        except (MedicamentoVencidoException, RecetaInvalidaException, VentaNoAutorizadaException) as e_negocio:
            print(f"\n[OPERACION DENEGADA POR SEGURIDAD SANITARIA]: {e_negocio}")
            AuditoriaService.registrar_evento(
                tipo="SEGURIDAD_VENTA_DENEGADA",
                detalle=str(e_negocio),
                usuario=vendedor_sel.nombre
            )
        except ValueError as e_val:
            print(f"\n[VALIDACION DE NEGOCIO]: {e_val}")

    if not venta.detalles:
        print("\nNo se agregaron productos al carrito. Venta cancelada.")
        return

    # 5. Guardar la transaccion completa junto con sus detalles en la base de datos
    try:
        id_venta_generada = VentaDAO.registrar_venta(venta)
        AuditoriaService.registrar_evento(
            tipo="VENTA_REGISTRADA_BD",
            detalle=f"Venta ID {id_venta_generada} persistida por total de ${venta.total:,.0f} CLP. Cliente: {venta.cliente.rut}",
            usuario=vendedor_sel.nombre
        )
        print(f"\n[EXITO] Venta registrada exitosamente en base de datos con Nro: {id_venta_generada}.")
        boleta_texto = generar_boleta_texto(venta, valor_dolar)
        print("\n" + boleta_texto)
    except Exception as e_bd:
        print(f"[ERROR TRANSACCIONAL] No se pudo guardar la venta en base de datos: {e_bd}")


# ==============================================================================
# MENU 2: GESTION CRUD DE MEDICAMENTOS (BASE DE DATOS)
# ==============================================================================

def menu_gestion_medicamentos():
    imprimir_encabezado("GESTION CRUD DE MEDICAMENTOS Y CATALOGO (SQLITE)")
    valor_dolar = APIService.obtener_dolar_tiempo_real()

    print(" 1. Listar Catalogo Completo de Medicamentos")
    print(" 2. Buscar Medicamento por Nombre")
    print(" 3. Crear Nuevo Medicamento")
    print(" 4. Actualizar Precio y Stock de Medicamento")
    print(" 5. Eliminar Medicamento del Catalogo")
    print(" 0. Volver al Menu Principal")

    opc = pedir_entero("\n Seleccione opcion [0-5]: ", minimo=0, maximo=5)

    if opc == 1:
        catalogo = MedicamentoDAO.listar_todos()
        mostrar_resumen_catalogo(catalogo, valor_dolar)

    elif opc == 2:
        nom = pedir_texto_no_vacio(" Ingrese nombre o termino a buscar: ")
        resultados = MedicamentoDAO.buscar_por_nombre(nom)
        if resultados:
            mostrar_resumen_catalogo(resultados, valor_dolar)
        else:
            print(f" No se encontraron medicamentos que contengan '{nom}'.")

    elif opc == 3:
        print("\n--- Creacion de Nuevo Medicamento ---")
        nombre = pedir_texto_no_vacio(" Nombre comercial del medicamento: ", min_longitud=3)
        precio_base = pedir_flotante(" Precio base (mayor a 0): ", minimo=0.01)
        stock = pedir_entero(" Stock inicial (entero >= 0): ", minimo=0)
        fecha_venc = pedir_fecha_vencimiento(" Fecha de vencimiento (AAAA-MM-DD): ")
        
        print(" Es producto importado con precio en USD?:")
        print("   1. Si (Calculo en base a Dolar en tiempo real)")
        print("   2. No (Precio directo en CLP)")
        opt_imp = pedir_entero("   Opcion [1-2]: ", minimo=1, maximo=2)
        es_imp = (opt_imp == 1)

        print(" Tipo de prescripcion medica:")
        print("   1. Venta Libre (MedSinReceta)")
        print("   2. Receta Simple (MedRecetaSimple)")
        print("   3. Medicamento Controlado (MedRecetaControlado)")
        opt_tipo = pedir_entero("   Opcion [1-3]: ", minimo=1, maximo=3)

        if opt_tipo == 1:
            nuevo_med = MedSinReceta(nombre, precio_base, stock, fecha_venc, es_imp)
        elif opt_tipo == 2:
            nuevo_med = MedRecetaSimple(nombre, precio_base, stock, fecha_venc, es_imp)
        else:
            nuevo_med = MedRecetaControlado(nombre, precio_base, stock, fecha_venc, es_imp, requiere_retencion=True)

        try:
            id_creado = MedicamentoDAO.crear(nuevo_med)
            AuditoriaService.registrar_evento(
                tipo="MEDICAMENTO_CREADO",
                detalle=f"Medicamento '{nombre}' (ID {id_creado}) creado exitosamente en SQLite."
            )
            print(f"[EXITO] Medicamento creado exitosamente con ID {id_creado}.")
        except Exception as e:
            print(f"[ERROR] No se pudo crear el medicamento: {e}")

    elif opc == 4:
        print("\n--- Actualizar Medicamento ---")
        id_m = pedir_entero(" Ingrese ID del medicamento a modificar: ", minimo=1)
        med = MedicamentoDAO.obtener_por_id(id_m)
        if not med:
            print(f" No existe medicamento con ID {id_m}.")
            return
        print(f" Medicamento seleccionado: {med.nombre} | Precio actual: {med.precio_base} | Stock actual: {med.stock}")
        nuevo_p = pedir_flotante(" Nuevo precio base: ", minimo=0.01)
        nuevo_s = pedir_entero(" Nuevo stock: ", minimo=0)
        med.precio_base = nuevo_p
        med.stock = nuevo_s
        if MedicamentoDAO.actualizar(med):
            AuditoriaService.registrar_evento(
                tipo="MEDICAMENTO_ACTUALIZADO",
                detalle=f"Medicamento ID {id_m} actualizado: precio={nuevo_p}, stock={nuevo_s}."
            )
            print("[EXITO] Medicamento actualizado correctamente en base de datos.")
        else:
            print("[ERROR] No se pudo actualizar el medicamento.")

    elif opc == 5:
        print("\n--- Eliminar Medicamento ---")
        id_m = pedir_entero(" Ingrese ID del medicamento a eliminar: ", minimo=1)
        med = MedicamentoDAO.obtener_por_id(id_m)
        if not med:
            print(f" No existe medicamento con ID {id_m}.")
            return
        print(f" Confirmar eliminacion de '{med.nombre}':")
        print("   1. Si, eliminar permanentemente de SQLite")
        print("   2. Cancelar")
        confirm = pedir_entero("   Opcion [1-2]: ", minimo=1, maximo=2)
        if confirm == 1:
            try:
                if MedicamentoDAO.eliminar(id_m):
                    AuditoriaService.registrar_evento(
                        tipo="MEDICAMENTO_ELIMINADO",
                        detalle=f"Medicamento '{med.nombre}' (ID {id_m}) eliminado de SQLite."
                    )
                    print(f"[EXITO] Medicamento ID {id_m} eliminado.")
                else:
                    print("[ERROR] No se pudo eliminar.")
            except Exception as e:
                print(f"[ERROR DE INTEGRIDAD] No se puede eliminar el medicamento porque posee registros asociados: {e}")


# ==============================================================================
# MENU 3: GESTION CRUD DE CLIENTES (BASE DE DATOS)
# ==============================================================================

def menu_gestion_clientes():
    imprimir_encabezado("GESTION CRUD DE CLIENTES (SQLITE)")
    print(" 1. Listar Todos los Clientes")
    print(" 2. Registrar Nuevo Cliente")
    print(" 3. Actualizar Nombre de Cliente")
    print(" 4. Eliminar Cliente")
    print(" 0. Volver al Menu Principal")

    opc = pedir_entero("\n Seleccione opcion [0-4]: ", minimo=0, maximo=4)

    if opc == 1:
        clientes = ClienteDAO.listar_todos()
        print(f"\n {'ID':<4} | {'RUT':<15} | {'Nombre Completo':<35}")
        print("-" * 60)
        for c in clientes:
            print(f" {c.id_cliente:<4} | {c.rut:<15} | {c.nombre:<35}")
        print("-" * 60)

    elif opc == 2:
        print("\n--- Nuevo Cliente ---")
        rut = pedir_rut_valido(" RUT Cliente: ")
        nom = pedir_texto_no_vacio(" Nombre completo: ", min_longitud=3)
        try:
            cli = Cliente(rut=rut, nombre=nom)
            id_creado = ClienteDAO.crear(cli)
            AuditoriaService.registrar_evento(
                tipo="CLIENTE_CREADO",
                detalle=f"Cliente '{nom}' (RUT {rut}) registrado con ID {id_creado}."
            )
            print(f"[EXITO] Cliente registrado con ID {id_creado}.")
        except Exception as e:
            print(f"[ERROR] No se pudo registrar cliente: {e}")

    elif opc == 3:
        print("\n--- Actualizar Cliente ---")
        id_c = pedir_entero(" ID Cliente a modificar: ", minimo=1)
        cli = ClienteDAO.obtener_por_id(id_c)
        if not cli:
            print(f" No existe cliente con ID {id_c}.")
            return
        print(f" Cliente: {cli.nombre} | RUT: {cli.rut}")
        nuevo_nom = pedir_texto_no_vacio(" Nuevo nombre completo: ", min_longitud=3)
        cli.nombre = nuevo_nom
        if ClienteDAO.actualizar(cli):
            print("[EXITO] Cliente actualizado correctamente en base de datos.")
        else:
            print("[ERROR] No se pudo actualizar cliente.")

    elif opc == 4:
        print("\n--- Eliminar Cliente ---")
        id_c = pedir_entero(" ID Cliente a eliminar: ", minimo=1)
        cli = ClienteDAO.obtener_por_id(id_c)
        if not cli:
            print(f" No existe cliente con ID {id_c}.")
            return
        try:
            if ClienteDAO.eliminar(id_c):
                print(f"[EXITO] Cliente '{cli.nombre}' eliminado.")
            else:
                print("[ERROR] No se pudo eliminar.")
        except Exception as e:
            print(f"[ERROR DE INTEGRIDAD] No se puede eliminar cliente porque tiene ventas asociadas: {e}")


# ==============================================================================
# MENU 4: FARMACIAS DE TURNO (SERVICIO MINSAL CON REQUESTS)
# ==============================================================================

def menu_farmacias_minsal():
    imprimir_encabezado("RED NACIONAL DE FARMACIAS DE TURNO - MINSAL (REQUESTS)")
    print("[SISTEMA] Consultando API del Ministerio de Salud en tiempo real...\n")
    comuna = input(" Ingrese comuna a filtrar (ej: Puente Alto, Santiago) o presione ENTER para ver todas: ").strip()
    locales = APIService.obtener_farmacias_turno(comuna_filtro=comuna if comuna else None)

    if not locales:
        print(f" No se encontraron farmacias de turno para '{comuna}'.")
        return

    print(f"\n Locales de Turno ({len(locales)} encontrados):")
    print(f" {'Comuna':<16} | {'Nombre Local':<32} | {'Direccion':<30} | {'Horario':<15}")
    print("-" * 100)
    for f in locales[:25]:
        print(f" {f['comuna'][:16]:<16} | {f['nombre'][:32]:<32} | {f['direccion'][:30]:<30} | {f['horario']:<15}")
    print("-" * 100)


# ==============================================================================
# MENU 5: AUTORIZACION PROFESIONAL DE RECETAS CONTROLADAS (QF)
# ==============================================================================

def menu_autorizar_receta(recetas_autorizadas: list):
    imprimir_encabezado("MODULO SANITARIO: AUTORIZACION Y RETENCION DE RECETAS (QF)")
    quimicos = PersonalDAO.listar_quimicos()
    if not quimicos:
        print(" No hay Quimicos Farmaceuticos disponibles en el sistema.")
        return

    qf = quimicos[0]
    print(f" Quimico Farmaceutico Titular: {qf.nombre} (Registro Sanitario: {qf.num_registro})\n")

    folio = pedir_texto_no_vacio(" Ingrese numero de folio de la receta medica: ")
    medico = pedir_texto_no_vacio(" Ingrese nombre completo del medico emisor: ")

    receta = Receta(numero_folio=folio, medico=medico, retenida=True)
    if qf.autorizar_controlado(receta):
        recetas_autorizadas.append(receta)
        AuditoriaService.registrar_evento(
            tipo="RECETA_AUTORIZADA",
            detalle=f"Receta Folio '{folio}' autorizada y retenida por QF {qf.nombre}.",
            usuario=qf.nombre
        )
        print(f"\n[EXITO] Receta Folio '{folio}' AUTORIZADA y RETENIDA exitosamente en el sistema.")
    else:
        print("\n[ERROR] No se pudo autorizar la receta.")


# ==============================================================================
# MENU 6: HISTORIAL DE VENTAS Y REEMISION DE BOLETAS (SQLITE)
# ==============================================================================

def menu_historial_ventas():
    imprimir_encabezado("HISTORIAL DE TRANSACCIONES Y REEMISION DE BOLETAS (SQLITE)")
    ventas = VentaDAO.listar_todas()

    if not ventas:
        print(" No hay ventas registradas en la base de datos.")
        return

    print(f" {'ID':<5} | {'Fecha':<20} | {'Cliente':<25} | {'Vendedor':<20} | {'Total CLP':>12}")
    print("-" * 90)
    for v in ventas:
        print(f" {v.id_venta:<5} | {v.fecha:<20} | {v.cliente.nombre[:25]:<25} | {v.vendedor.nombre[:20]:<20} | ${v.total:>11,.0f}")
    print("-" * 90)

    print("\nOpciones:")
    print(" 1. Reimprimir Boleta Electronica por ID de Venta")
    print(" 2. Eliminar/Anular Venta por ID")
    print(" 0. Regresar")
    opc = pedir_entero(" Seleccione opcion [0-2]: ", minimo=0, maximo=2)

    if opc == 1:
        id_sel = pedir_entero(" Ingrese ID de la venta: ", minimo=1)
        v_sel = VentaDAO.obtener_por_id(id_sel)
        if v_sel:
            valor_dolar = APIService.obtener_dolar_tiempo_real()
            print("\n" + generar_boleta_texto(v_sel, valor_dolar))
        else:
            print(f" No se encontro la venta con ID {id_sel}.")

    elif opc == 2:
        id_sel = pedir_entero(" Ingrese ID de la venta a eliminar: ", minimo=1)
        if VentaDAO.eliminar(id_sel):
            AuditoriaService.registrar_evento(
                tipo="VENTA_ELIMINADA",
                detalle=f"Venta ID {id_sel} eliminada de SQLite."
            )
            print(f"[EXITO] Venta ID {id_sel} eliminada correctamente.")
        else:
            print(f" No se encontro venta con ID {id_sel}.")


# ==============================================================================
# MENU 7: BITACORA DE AUDITORIA Y SEGURIDAD (SQLITE)
# ==============================================================================

def menu_auditoria():
    imprimir_encabezado("BITACORA DE AUDITORIA Y EVENTOS DE SEGURIDAD (SQLITE)")
    eventos = AuditoriaService.obtener_historial()

    if not eventos:
        print(" No hay eventos registrados en la bitacora de auditoria.")
        return

    print(f" {'ID':<4} | {'Fecha y Hora':<19} | {'Tipo Evento':<26} | {'Usuario':<16} | {'Detalle'}")
    print("-" * 105)
    for ev in eventos:
        print(f" {ev['id']:<4} | {ev['fecha']:<19} | {ev['tipo']:<26} | {ev['usuario'][:16]:<16} | {ev['detalle']}")
    print("-" * 105)


# ==============================================================================
# BUCLE PRINCIPAL DEL SISTEMA
# ==============================================================================

def main():
    # 1. Inicializacion automatica de SQLite con tablas y datos base
    inicializar_bd()

    AuditoriaService.registrar_evento(
        tipo="SISTEMA_INIT",
        detalle="Sistema Farmacia Cruz del Sur S.A. iniciado con persistencia SQLite y conexion segura a API."
    )

    recetas_autorizadas = []

    while True:
        # Consulta de indicador financiero con timeout y resiliencia
        valor_dolar_actual = APIService.obtener_dolar_tiempo_real()

        imprimir_encabezado("FARMACIA CRUZ DEL SUR S.A. - SISTEMA POS Y GESTOR SANITARIO")
        print(f"  Cotizacion USD Oficial (mindicador.cl / requests): ${valor_dolar_actual:,.2f} CLP")
        print("  " + "-" * 78)
        print("  1. Registrar Nueva Venta (Terminal POS)")
        print("  2. Gestion CRUD de Medicamentos e Inventario (SQLite)")
        print("  3. Gestion CRUD de Clientes (SQLite)")
        print("  4. Red Nacional de Farmacias de Turno (MINSAL / requests)")
        print("  5. Modulo Sanitario de Autorizacion de Recetas (QF)")
        print("  6. Historial de Transacciones y Reemision de Boletas (SQLite)")
        print("  7. Bitacora de Auditoria y Seguridad (SQLite)")
        print("  0. Salir del Sistema")
        print("  " + "-" * 78)

        opcion = pedir_entero(" Seleccione opcion [0-7]: ", minimo=0, maximo=7)

        if opcion == 1:
            menu_pos_venta(recetas_autorizadas)
        elif opcion == 2:
            menu_gestion_medicamentos()
        elif opcion == 3:
            menu_gestion_clientes()
        elif opcion == 4:
            menu_farmacias_minsal()
        elif opcion == 5:
            menu_autorizar_receta(recetas_autorizadas)
        elif opcion == 6:
            menu_historial_ventas()
        elif opcion == 7:
            menu_auditoria()
        elif opcion == 0:
            print("\nCerrando sesion en Sistema Farmacia Cruz del Sur S.A. Hasta pronto.")
            sys.exit(0)

        input("\nPresione ENTER para volver al menu principal...")


if __name__ == "__main__":
    main()
