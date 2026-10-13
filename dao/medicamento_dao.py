from dao.database import obtener_conexion
from model.medicamento import Medicamento
from model.med_sin_receta import MedSinReceta
from model.med_receta_simple import MedRecetaSimple
from model.med_receta_controlado import MedRecetaControlado


class MedicamentoDAO:
    """DAO para operaciones CRUD de la entidad principal Medicamento en SQLite."""

    @staticmethod
    def _fila_a_objeto(fila) -> Medicamento:
        """Instancia la subclase correspondiente del modelo a partir del registro."""
        tipo = fila["tipo_medicamento"]
        id_med = fila["id_medicamento"]
        nombre = fila["nombre"]
        precio_base = fila["precio_base"]
        stock = fila["stock"]
        fecha_venc = fila["fecha_vencimiento"]
        es_importado = bool(fila["es_importado"])

        if tipo == "CONTROLADO":
            requiere_ret = bool(fila["requiere_retencion"])
            return MedRecetaControlado(
                nombre=nombre,
                precio_base=precio_base,
                stock=stock,
                fecha_vencimiento=fecha_venc,
                es_importado=es_importado,
                requiere_retencion=requiere_ret,
                id_medicamento=id_med
            )
        elif tipo == "RECETA_SIMPLE":
            return MedRecetaSimple(
                nombre=nombre,
                precio_base=precio_base,
                stock=stock,
                fecha_vencimiento=fecha_venc,
                es_importado=es_importado,
                id_medicamento=id_med
            )
        else:
            return MedSinReceta(
                nombre=nombre,
                precio_base=precio_base,
                stock=stock,
                fecha_vencimiento=fecha_venc,
                es_importado=es_importado,
                id_medicamento=id_med
            )

    @classmethod
    def crear(cls, med: Medicamento) -> int:
        """Inserta un nuevo medicamento en la base de datos de forma parametrizada."""
        requiere_ret = 1 if med.requiere_retencion else 0
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO medicamentos (
                    nombre, precio_base, stock, fecha_vencimiento, es_importado, tipo_medicamento, requiere_retencion
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                med.nombre,
                med.precio_base,
                med.stock,
                med.fecha_vencimiento,
                1 if med.es_importado else 0,
                med.tipo_medicamento,
                requiere_ret
            ))
            conn.commit()
            med.id_medicamento = cursor.lastrowid
            return med.id_medicamento

    @classmethod
    def obtener_por_id(cls, id_medicamento: int) -> Medicamento:
        """Obtiene un medicamento por su ID parametrizado."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicamentos WHERE id_medicamento = ?", (id_medicamento,))
            fila = cursor.fetchone()
            if fila:
                return cls._fila_a_objeto(fila)
            return None

    @classmethod
    def listar_todos(cls) -> list:
        """Retorna todos los medicamentos como lista de objetos del modelo."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medicamentos ORDER BY id_medicamento ASC")
            filas = cursor.fetchall()
            return [cls._fila_a_objeto(fila) for fila in filas]

    @classmethod
    def buscar_por_nombre(cls, termino: str) -> list:
        """Busca medicamentos por nombre utilizando LIKE parametrizado."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            patron = f"%{termino}%"
            cursor.execute("SELECT * FROM medicamentos WHERE nombre LIKE ? ORDER BY nombre ASC", (patron,))
            filas = cursor.fetchall()
            return [cls._fila_a_objeto(fila) for fila in filas]

    @classmethod
    def actualizar(cls, med: Medicamento) -> bool:
        """Actualiza un medicamento existente mediante consulta parametrizada."""
        requiere_ret = 1 if med.requiere_retencion else 0
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE medicamentos
                SET nombre = ?,
                    precio_base = ?,
                    stock = ?,
                    fecha_vencimiento = ?,
                    es_importado = ?,
                    tipo_medicamento = ?,
                    requiere_retencion = ?
                WHERE id_medicamento = ?
            """, (
                med.nombre,
                med.precio_base,
                med.stock,
                med.fecha_vencimiento,
                1 if med.es_importado else 0,
                med.tipo_medicamento,
                requiere_ret,
                med.id_medicamento
            ))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def eliminar(cls, id_medicamento: int) -> bool:
        """Elimina un medicamento por ID de forma parametrizada."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM medicamentos WHERE id_medicamento = ?", (id_medicamento,))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def descontar_stock(cls, id_medicamento: int, cantidad: int) -> bool:
        """Descuenta stock directamente en la BD con consulta parametrizada y verificacion."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE medicamentos
                SET stock = stock - ?
                WHERE id_medicamento = ? AND stock >= ?
            """, (cantidad, id_medicamento, cantidad))
            conn.commit()
            return cursor.rowcount > 0
