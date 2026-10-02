from model.med_sin_receta import MedSinReceta
from model.med_receta_simple import MedRecetaSimple
from model.med_receta_controlado import MedRecetaControlado


class InventarioService:
    """
    Servicio de gestión de inventario y stock de medicamentos de la farmacia.
    """
    def __init__(self):
        self._catalogo = []
        self._cargar_catalogo_inicial()

    def _cargar_catalogo_inicial(self):
        """Carga un catálogo real de medicamentos con códigos de barra simulados."""
        self._catalogo = [
            # Venta Libre
            MedSinReceta(nombre="Paracetamol 500mg (16 comprimidos)", precio_base=1890.0, stock=120, fecha_vencimiento="2027-12-31"),
            MedSinReceta(nombre="Ibuprofeno 400mg (20 cápsulas)", precio_base=2490.0, stock=85, fecha_vencimiento="2027-11-15"),
            MedSinReceta(nombre="Tapsin Periodo Noche (6 sobres)", precio_base=3290.0, stock=45, fecha_vencimiento="2027-08-20"),
            MedSinReceta(nombre="Aspirina 100mg (VENCIDA TEST)", precio_base=1500.0, stock=15, fecha_vencimiento="2023-01-01"),

            # Receta Simple
            MedRecetaSimple(nombre="Amoxicilina 500mg Jarabe (Importado USD)", precio_base=6.5, stock=40, fecha_vencimiento="2027-05-10", es_importado=True),
            MedRecetaSimple(nombre="Loratadina 10mg (30 comprimidos)", precio_base=4890.0, stock=60, fecha_vencimiento="2028-02-28"),
            MedRecetaSimple(nombre="Losartán Potásico 50mg (30 comp)", precio_base=5990.0, stock=75, fecha_vencimiento="2027-10-18"),
            MedRecetaSimple(nombre="Omeprazol 20mg (28 cápsulas)", precio_base=3790.0, stock=90, fecha_vencimiento="2027-09-30"),

            # Medicamentos Controlados
            MedRecetaControlado(nombre="Clonazepam 2mg (30 comprimidos)", precio_base=9990.0, stock=25, fecha_vencimiento="2028-06-15", requiere_retencion=True),
            MedRecetaControlado(nombre="Tramadol 50mg (20 cápsulas)", precio_base=13490.0, stock=18, fecha_vencimiento="2027-12-01", requiere_retencion=True),
            MedRecetaControlado(nombre="Alprazolam 0.5mg (30 comp)", precio_base=11290.0, stock=20, fecha_vencimiento="2028-04-10", requiere_retencion=True)
        ]

    def listar_todos(self) -> list:
        return self._catalogo

    def buscar_por_nombre(self, termino: str) -> list:
        termino_lower = termino.lower()
        return [m for m in self._catalogo if termino_lower in m.nombre.lower()]

    def obtener_por_id(self, idx: int):
        if 0 <= idx < len(self._catalogo):
            return self._catalogo[idx]
        return None

    def agregar_medicamento(self, medicamento):
        self._catalogo.append(medicamento)

    def obtener_vencidos(self) -> list:
        return [m for m in self._catalogo if m.esta_vencido()]
