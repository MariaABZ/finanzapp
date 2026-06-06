import calendar
from decimal import Decimal
from datetime import date

def ingreso_primera_quincena(monto_mensual: Decimal, porcentaje: int) -> Decimal:
    return round(monto_mensual * Decimal(porcentaje) / Decimal(100), 2)

def ingreso_segunda_quincena(monto_mensual: Decimal, porcentaje: int) -> Decimal:
    return round(monto_mensual * Decimal(100 - porcentaje) / Decimal(100), 2)

def calcular_ingreso_quincena(ingresos_activos: list, numero_quincena: int) -> Decimal:
    if numero_quincena not in (1, 2):
        raise ValueError("numero_quincena debe ser 1 o 2")
    total = Decimal("0")
    for ingreso in ingresos_activos:
        if numero_quincena == 1:
            total += ingreso_primera_quincena(ingreso.monto_mensual, ingreso.porcentaje_primera_quincena)
        else:
            total += ingreso_segunda_quincena(ingreso.monto_mensual, ingreso.porcentaje_primera_quincena)
    return total

def fechas_quincena(anio: int, mes: int, numero: int) -> tuple[date, date]:
    if numero == 1:
        return date(anio, mes, 1), date(anio, mes, 15)
    else:
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        return date(anio, mes, 16), date(anio, mes, ultimo_dia)

def total_ingresos_mensuales(ingresos_activos: list) -> Decimal:
    return sum((i.monto_mensual for i in ingresos_activos), start=Decimal("0"))
