import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "farmacia.db")


def obtener_conexion() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_bd():
    """Crea las tablas en SQLite si no existen y siembra datos iniciales si estan vacias."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()

        # Tabla de Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL
            )
        """)

        # Tabla de Medicamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicamentos (
                id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                precio_base REAL NOT NULL,
                stock INTEGER NOT NULL,
                fecha_vencimiento TEXT NOT NULL,
                es_importado INTEGER NOT NULL DEFAULT 0,
                tipo_medicamento TEXT NOT NULL,
                requiere_retencion INTEGER NOT NULL DEFAULT 0
            )
        """)

        # Tabla de Vendedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendedores (
                id_vendedor INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                caja_asignada INTEGER NOT NULL
            )
        """)

        # Tabla de Quimicos Farmaceuticos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quimicos (
                id_quimico INTEGER PRIMARY KEY AUTOINCREMENT,
                rut TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                num_registro TEXT NOT NULL
            )
        """)

        # Tabla de Ventas (Transaccion Maestro)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                id_vendedor INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente),
                FOREIGN KEY (id_vendedor) REFERENCES vendedores (id_vendedor)
            )
        """)

        # Tabla de Detalles de Venta (Lineas de Detalle)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                id_medicamento INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                folio_receta TEXT,
                medico_receta TEXT,
                receta_retenida INTEGER DEFAULT 0,
                receta_autorizada INTEGER DEFAULT 0,
                FOREIGN KEY (id_venta) REFERENCES ventas (id_venta) ON DELETE CASCADE,
                FOREIGN KEY (id_medicamento) REFERENCES medicamentos (id_medicamento)
            )
        """)

        # Tabla de Auditoria de Eventos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo TEXT NOT NULL,
                detalle TEXT NOT NULL,
                usuario TEXT NOT NULL
            )
        """)

        conn.commit()

    _sembrar_datos_iniciales()


def _sembrar_datos_iniciales():
    """Siembra datos iniciales de catalogo y personal si las tablas estan vacias."""
    with obtener_conexion() as conn:
        cursor = conn.cursor()

        # Sembrar Vendedores si no hay registros
        cursor.execute("SELECT COUNT(*) as cant FROM vendedores")
        if cursor.fetchone()["cant"] == 0:
            vendedores_ini = [
                ("19.876.543-0", "Juan Perez", 1),
                ("18.999.888-0", "Camila Torres", 2)
            ]
            cursor.executemany(
                "INSERT INTO vendedores (rut, nombre, caja_asignada) VALUES (?, ?, ?)",
                vendedores_ini
            )

        # Sembrar Quimico Farmaceutico si no hay registros
        cursor.execute("SELECT COUNT(*) as cant FROM quimicos")
        if cursor.fetchone()["cant"] == 0:
            quimicos_ini = [
                ("15.432.109-8", "Dra. Maria Gonzalez", "QF-88421")
            ]
            cursor.executemany(
                "INSERT INTO quimicos (rut, nombre, num_registro) VALUES (?, ?, ?)",
                quimicos_ini
            )

        # Sembrar Clientes base si no hay registros
        cursor.execute("SELECT COUNT(*) as cant FROM clientes")
        if cursor.fetchone()["cant"] == 0:
            clientes_ini = [
                ("18.123.456-3", "Pedro Tapia"),
                ("12.345.678-5", "Andrea Silva")
            ]
            cursor.executemany(
                "INSERT INTO clientes (rut, nombre) VALUES (?, ?)",
                clientes_ini
            )

        # Sembrar Catalogo de Medicamentos si no hay registros
        cursor.execute("SELECT COUNT(*) as cant FROM medicamentos")
        if cursor.fetchone()["cant"] == 0:
            medicamentos_ini = [
                # Medicamentos de Venta Libre
                ("Paracetamol 500mg (16 comprimidos)", 1890.0, 120, "2027-12-31", 0, "LIBRE", 0),
                ("Ibuprofeno 400mg (20 capsulas)", 2490.0, 85, "2027-11-15", 0, "LIBRE", 0),
                ("Tapsin Periodo Noche (6 sobres)", 3290.0, 45, "2027-08-20", 0, "LIBRE", 0),
                ("Aspirina 100mg (VENCIDA TEST)", 1500.0, 15, "2023-01-01", 0, "LIBRE", 0),

                # Medicamentos con Receta Simple
                ("Amoxicilina 500mg Jarabe (Importado USD)", 6.5, 40, "2027-05-10", 1, "RECETA_SIMPLE", 0),
                ("Loratadina 10mg (30 comprimidos)", 4890.0, 60, "2028-02-28", 0, "RECETA_SIMPLE", 0),
                ("Losartan Potasico 50mg (30 comp)", 5990.0, 75, "2027-10-18", 0, "RECETA_SIMPLE", 0),
                ("Omeprazol 20mg (28 capsulas)", 3790.0, 90, "2027-09-30", 0, "RECETA_SIMPLE", 0),

                # Medicamentos Controlados
                ("Clonazepam 2mg (30 comprimidos)", 9990.0, 25, "2028-06-15", 0, "CONTROLADO", 1),
                ("Tramadol 50mg (20 capsulas)", 13490.0, 18, "2027-12-01", 0, "CONTROLADO", 1),
                ("Alprazolam 0.5mg (30 comp)", 11290.0, 20, "2028-04-10", 0, "CONTROLADO", 1)
            ]
            cursor.executemany("""
                INSERT INTO medicamentos (
                    nombre, precio_base, stock, fecha_vencimiento, es_importado, tipo_medicamento, requiere_retencion
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, medicamentos_ini)

        conn.commit()
