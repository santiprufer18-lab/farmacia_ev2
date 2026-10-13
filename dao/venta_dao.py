from dao.database import obtener_conexion
from dao.cliente_dao import ClienteDAO
from dao.medicamento_dao import MedicamentoDAO
from dao.personal_dao import PersonalDAO
from model.venta import Venta
from model.detalle_venta import DetalleVenta
from model.receta import Receta


class VentaDAO:

    @classmethod
    def registrar_venta(cls, venta: Venta) -> int:
        if not venta.detalles:
            raise ValueError("No se puede registrar una venta sin lineas de detalle.")

        # Asegurar ID del cliente
        id_cliente = venta.cliente.id_cliente
        if not id_cliente:
            cliente_db = ClienteDAO.obtener_por_rut(venta.cliente.rut)
            if cliente_db:
                id_cliente = cliente_db.id_cliente
                venta.cliente.id_cliente = id_cliente
            else:
                id_cliente = ClienteDAO.crear(venta.cliente)

        # Asegurar ID del vendedor
        id_vendedor = getattr(venta.vendedor, "id_vendedor", None)
        if not id_vendedor:
            id_vendedor = 1  # Vendedor por defecto si no esta mapeado

        with obtener_conexion() as conn:
            cursor = conn.cursor()
            try:
                # 1. Insertar cabecera de la venta (transaccion maestra)
                cursor.execute("""
                    INSERT INTO ventas (id_cliente, id_vendedor, fecha, total)
                    VALUES (?, ?, ?, ?)
                """, (
                    id_cliente,
                    id_vendedor,
                    venta.fecha,
                    venta.total
                ))
                id_venta = cursor.lastrowid
                venta.id_venta = id_venta

                # 2. Insertar cada linea de detalle y actualizar stock
                for det in venta.detalles:
                    folio_r = det.receta.numero_folio if det.receta else None
                    medico_r = det.receta.medico if det.receta else None
                    ret_r = 1 if (det.receta and det.receta.retenida) else 0
                    aut_r = 1 if (det.receta and det.receta.autorizada_por_quimico) else 0

                    cursor.execute("""
                        INSERT INTO detalles_venta (
                            id_venta, id_medicamento, cantidad, precio_unitario, subtotal,
                            folio_receta, medico_receta, receta_retenida, receta_autorizada
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_venta,
                        det.medicamento.id_medicamento,
                        det.cantidad,
                        det.precio_unitario,
                        det.subtotal,
                        folio_r,
                        medico_r,
                        ret_r,
                        aut_r
                    ))
                    det.id_detalle = cursor.lastrowid
                    det.id_venta = id_venta

                    # Actualizar stock del medicamento en la base de datos
                    cursor.execute("""
                        UPDATE medicamentos
                        SET stock = stock - ?
                        WHERE id_medicamento = ?
                    """, (det.cantidad, det.medicamento.id_medicamento))

                conn.commit()
                return id_venta
            except Exception as e:
                conn.rollback()
                raise RuntimeError(f"Error al registrar la transaccion de venta en BD: {e}")

    @classmethod
    def obtener_por_id(cls, id_venta: int) -> Venta:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id_venta, v.id_cliente, v.id_vendedor, v.fecha, v.total,
                       c.rut as c_rut, c.nombre as c_nom,
                       vend.rut as v_rut, vend.nombre as v_nom, vend.caja_asignada as v_caja
                FROM ventas v
                JOIN clientes c ON v.id_cliente = c.id_cliente
                JOIN vendedores vend ON v.id_vendedor = vend.id_vendedor
                WHERE v.id_venta = ?
            """, (id_venta,))
            fila_v = cursor.fetchone()
            if not fila_v:
                return None

            cliente = ClienteDAO.obtener_por_id(fila_v["id_cliente"])
            vendedor = PersonalDAO.obtener_vendedor_por_id(fila_v["id_vendedor"])
            venta = Venta(
                cliente=cliente,
                vendedor=vendedor,
                fecha=fila_v["fecha"],
                total=fila_v["total"],
                id_venta=fila_v["id_venta"]
            )

            # Cargar lineas de detalle
            cursor.execute("""
                SELECT * FROM detalles_venta WHERE id_venta = ? ORDER BY id_detalle ASC
            """, (id_venta,))
            filas_det = cursor.fetchall()
            for fd in filas_det:
                med = MedicamentoDAO.obtener_por_id(fd["id_medicamento"])
                receta = None
                if fd["folio_receta"] and fd["medico_receta"]:
                    receta = Receta(
                        numero_folio=fd["folio_receta"],
                        medico=fd["medico_receta"],
                        retenida=bool(fd["receta_retenida"]),
                        autorizada_por_quimico=bool(fd["receta_autorizada"])
                    )
                det = DetalleVenta(
                    medicamento=med,
                    cantidad=fd["cantidad"],
                    receta=receta,
                    precio_unitario=fd["precio_unitario"],
                    id_detalle=fd["id_detalle"],
                    id_venta=id_venta
                )
                venta.agregar_detalle_existente(det)

            return venta

    @classmethod
    def listar_todas(cls) -> list:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_venta FROM ventas ORDER BY id_venta DESC")
            filas = cursor.fetchall()
            ventas = []
            for f in filas:
                v = cls.obtener_por_id(f["id_venta"])
                if v:
                    ventas.append(v)
            return ventas

    @classmethod
    def eliminar(cls, id_venta: int) -> bool:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ventas WHERE id_venta = ?", (id_venta,))
            conn.commit()
            return cursor.rowcount > 0
