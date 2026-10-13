from dao.database import obtener_conexion
from model.vendedor import Vendedor
from model.quimico_farmaceutico import QuimicoFarmaceutico


class PersonalDAO:
    """DAO para operaciones de personal (Vendedores y Quimicos Farmaceuticos) en SQLite."""

    @classmethod
    def listar_vendedores(cls) -> list:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vendedores ORDER BY id_vendedor ASC")
            filas = cursor.fetchall()
            return [
                Vendedor(
                    rut=f["rut"],
                    nombre=f["nombre"],
                    caja_asignada=f["caja_asignada"],
                    id_vendedor=f["id_vendedor"]
                )
                for f in filas
            ]

    @classmethod
    def obtener_vendedor_por_id(cls, id_vendedor: int) -> Vendedor:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vendedores WHERE id_vendedor = ?", (id_vendedor,))
            f = cursor.fetchone()
            if f:
                return Vendedor(
                    rut=f["rut"],
                    nombre=f["nombre"],
                    caja_asignada=f["caja_asignada"],
                    id_vendedor=f["id_vendedor"]
                )
            return None

    @classmethod
    def listar_quimicos(cls) -> list:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quimicos ORDER BY id_quimico ASC")
            filas = cursor.fetchall()
            return [
                QuimicoFarmaceutico(
                    rut=f["rut"],
                    nombre=f["nombre"],
                    num_registro=f["num_registro"],
                    id_quimico=f["id_quimico"]
                )
                for f in filas
            ]

    @classmethod
    def obtener_quimico_por_id(cls, id_quimico: int) -> QuimicoFarmaceutico:
        with obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quimicos WHERE id_quimico = ?", (id_quimico,))
            f = cursor.fetchone()
            if f:
                return QuimicoFarmaceutico(
                    rut=f["rut"],
                    nombre=f["nombre"],
                    num_registro=f["num_registro"],
                    id_quimico=f["id_quimico"]
                )
            return None
