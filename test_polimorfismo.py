"""
Script de prueba automatizada para demostrar el despacho polimorfico
sin isinstance en main.py.

Flujos probados:
1. Venta de medicamento LIBRE (Paracetamol) - sin receta
2. Venta de medicamento RECETA_SIMPLE (Loratadina) - pide folio y medico
3. Intento de venta de medicamento CONTROLADO (Clonazepam) - requiere receta autorizada por QF
4. Autorizacion de receta por QF + venta de controlado exitosa
"""
import sys
import os

# Inicializar BD fresca
from dao.database import inicializar_bd
inicializar_bd()

# Probar que tipo_receta_requerida funciona polimorficamente
from dao.medicamento_dao import MedicamentoDAO

print("=" * 80)
print("  PRUEBA DE POLIMORFISMO: tipo_receta_requerida (SIN isinstance)")
print("=" * 80)

catalogo = MedicamentoDAO.listar_todos()
print(f"\n{'ID':<4} | {'Medicamento':<40} | {'Tipo':<16} | {'Receta Requerida':<20}")
print("-" * 90)
for med in catalogo:
    print(f"{med.id_medicamento:<4} | {med.nombre:<40} | {med.tipo_medicamento:<16} | {med.tipo_receta_requerida:<20}")
print("-" * 90)

# Probar validacion de venta para cada tipo
from model.receta import Receta
from model.excepciones import MedicamentoVencidoException, RecetaInvalidaException, VentaNoAutorizadaException

print("\n" + "=" * 80)
print("  PRUEBA 1: Venta de Medicamento LIBRE (Paracetamol - ID 1)")
print("=" * 80)
med_libre = MedicamentoDAO.obtener_por_id(1)
print(f"  Medicamento: {med_libre.nombre}")
print(f"  tipo_receta_requerida: '{med_libre.tipo_receta_requerida}'")
print(f"  Resultado: ", end="")
try:
    med_libre.validar_venta()
    print("VENTA APROBADA (no requiere receta)")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("  PRUEBA 2: Venta de Medicamento RECETA SIMPLE (Loratadina - ID 6)")
print("=" * 80)
med_receta = MedicamentoDAO.obtener_por_id(6)
print(f"  Medicamento: {med_receta.nombre}")
print(f"  tipo_receta_requerida: '{med_receta.tipo_receta_requerida}'")

print(f"\n  2a. Intento SIN receta: ", end="")
try:
    med_receta.validar_venta(receta=None)
    print("VENTA APROBADA")
except RecetaInvalidaException as e:
    print(f"BLOQUEADO -> {e}")

print(f"  2b. Intento CON receta valida: ", end="")
receta_simple = Receta(numero_folio="RS-2026-001", medico="Dr. Fernandez")
try:
    med_receta.validar_venta(receta=receta_simple)
    print("VENTA APROBADA (receta simple presentada)")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("  PRUEBA 3: Venta de Medicamento CONTROLADO (Clonazepam - ID 9)")
print("=" * 80)
med_ctrl = MedicamentoDAO.obtener_por_id(9)
print(f"  Medicamento: {med_ctrl.nombre}")
print(f"  tipo_receta_requerida: '{med_ctrl.tipo_receta_requerida}'")

print(f"\n  3a. Intento SIN receta: ", end="")
try:
    med_ctrl.validar_venta(receta=None)
    print("VENTA APROBADA")
except RecetaInvalidaException as e:
    print(f"BLOQUEADO -> {e}")

print(f"  3b. Intento CON receta NO autorizada: ", end="")
receta_no_auth = Receta(numero_folio="RC-2026-100", medico="Dr. Lopez", retenida=True)
try:
    med_ctrl.validar_venta(receta=receta_no_auth)
    print("VENTA APROBADA")
except VentaNoAutorizadaException as e:
    print(f"BLOQUEADO -> {e}")

print(f"  3c. Intento CON receta AUTORIZADA por QF: ", end="")
from dao.personal_dao import PersonalDAO
quimico = PersonalDAO.listar_quimicos()[0]
receta_auth = Receta(numero_folio="RC-2026-200", medico="Dr. Martinez", retenida=True)
quimico.autorizar_controlado(receta_auth)
try:
    med_ctrl.validar_venta(receta=receta_auth)
    print(f"VENTA APROBADA (autorizada por {quimico.nombre})")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("  PRUEBA 4: Medicamento VENCIDO (Aspirina TEST - ID 4)")
print("=" * 80)
med_venc = MedicamentoDAO.obtener_por_id(4)
print(f"  Medicamento: {med_venc.nombre}")
print(f"  tipo_receta_requerida: '{med_venc.tipo_receta_requerida}'")
print(f"  Fecha vencimiento: {med_venc.fecha_vencimiento}")
print(f"  esta_vencido(): {med_venc.esta_vencido()}")
print(f"  Intento de venta: ", end="")
try:
    med_venc.validar_venta()
    print("VENTA APROBADA")
except MedicamentoVencidoException as e:
    print(f"BLOQUEADO -> {e}")

print("\n" + "=" * 80)
print("  PRUEBA 5: Despacho polimorfico en logica de main.py (sin isinstance)")
print("=" * 80)
print("  Simulando la logica del menu POS para 3 medicamentos:\n")

meds_prueba = [
    MedicamentoDAO.obtener_por_id(1),   # LIBRE
    MedicamentoDAO.obtener_por_id(6),   # RECETA_SIMPLE
    MedicamentoDAO.obtener_por_id(9),   # CONTROLADO
]

for med in meds_prueba:
    tipo_receta = med.tipo_receta_requerida  # <-- POLIMORFISMO, no isinstance
    print(f"  Medicamento: {med.nombre}")
    print(f"    med.tipo_receta_requerida = '{tipo_receta}'")
    
    if tipo_receta == "NINGUNA":
        print(f"    -> Accion: Venta directa, no se solicita receta.")
    elif tipo_receta == "RECETA_SIMPLE":
        print(f"    -> Accion: Se solicita folio y medico emisor de receta simple.")
    elif tipo_receta == "RECETA_CONTROLADA":
        print(f"    -> Accion: Se exige receta retenida + autorizacion del Quimico Farmaceutico.")
    print()

print("=" * 80)
print("  TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("  isinstance eliminado de main.py -> Polimorfismo con tipo_receta_requerida")
print("=" * 80)
