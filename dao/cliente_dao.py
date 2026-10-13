from dao.database import obtener_conexion
from model.cliente import Cliente


class ClienteDAO:
    """DAO para operaciones CRUD de la entidad principal Cliente en SQLite."""

    @staticmethod
    def _fila_a_objeto(fila) -> Cliente:
        return Cliente(
            rut=fila["rut"],
            nombre=fila["nombre"],
            id_cliente=fila["id_cliente"]
        )

    @classmethod
    def crear(cls, cliente: Cliente) -> int:
        """Inserta un nuevo cliente de forma parametrizada."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (rut, nombre) VALUES (?, ?)",
                (cliente.rut, cliente.nombre)
            )
            conn.commit()
            cliente.id_cliente = cursor.lastrowid
            return cliente.id_cliente

    @classmethod
    def obtener_por_id(cls, id_cliente: int) -> Cliente:
        """Obtiene un cliente por ID de forma parametrizada."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))
            fila = cursor.fetchone()
            if fila:
                return cls._fila_a_objeto(fila)
            return None

    @classmethod
    def obtener_por_rut(cls, rut: str) -> Cliente:
        """Obtiene un cliente por RUT de forma parametrizada."""
        val_limpio = str(rut).replace(".", "").replace("-", "").strip().upper()
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes")
            filas = cursor.fetchall()
            for fila in filas:
                rut_db = str(fila["rut"]).replace(".", "").replace("-", "").strip().upper()
                if rut_db == val_limpio:
                    return cls._fila_a_objeto(fila)
            return None

    @classmethod
    def listar_todos(cls) -> list:
        """Lista todos los clientes como instancias de Cliente."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes ORDER BY id_cliente ASC")
            filas = cursor.fetchall()
            return [cls._fila_a_objeto(fila) for fila in filas]

    @classmethod
    def actualizar(cls, cliente: Cliente) -> bool:
        """Actualiza los datos de un cliente de forma parametrizada."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET rut = ?, nombre = ? WHERE id_cliente = ?",
                (cliente.rut, cliente.nombre, cliente.id_cliente)
            )
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    def eliminar(cls, id_cliente: int) -> bool:
        """Elimina un cliente por su ID de forma parametrizada."""
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
            conn.commit()
            return cursor.rowcount > 0
