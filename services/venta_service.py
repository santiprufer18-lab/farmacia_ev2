from datetime import datetime
from model.venta import Venta
from services.auditoria_service import AuditoriaService


class VentaService:
    """
    Servicio de gestión del proceso de venta (POS) y emisión de comprobantes fiscales de farmacia.
    """
    def __init__(self):
        self._ventas_realizadas = []

    def registrar_venta(self, venta: Venta) -> bool:
        if not venta.detalles:
            return False
        self._ventas_realizadas.append(venta)
        AuditoriaService.registrar_evento(
            tipo="VENTA_REGISTRADA",
            detalle=f"Venta registrada por Total ${venta.total:,.0f} CLP. Cliente RUT: {venta.cliente.rut}",
            usuario=venta.vendedor.nombre
        )
        return True

    def listar_ventas(self) -> list:
        return self._ventas_realizadas

    @staticmethod
    def generar_boleta_texto(venta: Venta, valor_dolar: float = 950.0) -> str:
        subtotal_neto = venta.total / 1.19
        iva = venta.total - subtotal_neto

        lineas = []
        lineas.append("=" * 64)
        lineas.append("                 FARMACIA CRUZ DEL SUR S.A.")
        lineas.append("             R.U.T.: 76.543.210-K - GIRO: FARMACIA")
        lineas.append("           Av. Concha y Toro 1340, Puente Alto, Santiago")
        lineas.append("=" * 64)
        lineas.append(" BOLETA ELECTRÓNICA DE VENTA")
        lineas.append(f" Fecha Emisión : {venta.fecha}")
        lineas.append(f" Cliente        : {venta.cliente.nombre}")
        lineas.append(f" RUT Cliente    : {venta.cliente.rut}")
        lineas.append(f" Atendido Por   : {venta.vendedor.nombre} (Caja {venta.vendedor.caja_asignada})")
        lineas.append("-" * 64)
        lineas.append(f" {'CANT':<4} | {'DESCRIPCIÓN':<34} | {'P.UNIT':>8} | {'SUBTOTAL':>9}")
        lineas.append("-" * 64)
        
        for det in venta.detalles:
            p_unit = det.medicamento.get_precio_final(valor_dolar)
            lineas.append(f" {det.cantidad:<4} | {det.medicamento.nombre[:34]:<34} | ${p_unit:>7,.0f} | ${det.subtotal:>8,.0f}")
        
        lineas.append("-" * 64)
        lineas.append(f" NETO (19% IVA incluido) : ${subtotal_neto:>39,.0f} CLP")
        lineas.append(f" IVA (19%)              : ${iva:>39,.0f} CLP")
        lineas.append(f" TOTAL A PAGAR          : ${venta.total:>39,.0f} CLP")
        lineas.append("=" * 64)
        lineas.append("          ¡Gracias por su compra en Farmacia Cruz del Sur!")
        lineas.append("     Timbre Electrónico SII - Res. N° 80 del 2026 - Verifique en sii.cl")
        lineas.append("=" * 64)
        return "\n".join(lineas)
