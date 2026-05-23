from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock

from app.services.ingreso_service import (
    ingreso_primera_quincena,
    ingreso_segunda_quincena,
    calcular_ingreso_quincena,
    fechas_quincena,
    total_ingresos_mensuales,
)


# --- ingreso_primera_quincena ---

def test_primera_quincena_50_porciento():
    assert ingreso_primera_quincena(Decimal("4000000"), 50) == Decimal("2000000.00")


def test_primera_quincena_60_porciento():
    assert ingreso_primera_quincena(Decimal("3000000"), 60) == Decimal("1800000.00")


def test_segunda_quincena_es_complemento():
    monto = Decimal("4000000")
    pct = 50
    assert ingreso_primera_quincena(monto, pct) + ingreso_segunda_quincena(monto, pct) == monto


# --- calcular_ingreso_quincena ---

def _make_ingreso(monto: str, porcentaje: int = 50):
    m = MagicMock()
    m.monto_mensual = Decimal(monto)
    m.porcentaje_primera_quincena = porcentaje
    return m


def test_calcular_sin_ingresos():
    assert calcular_ingreso_quincena([], 1) == Decimal("0")


def test_calcular_un_ingreso_primera_quincena():
    ingresos = [_make_ingreso("4000000", 50)]
    assert calcular_ingreso_quincena(ingresos, 1) == Decimal("2000000.00")


def test_calcular_un_ingreso_segunda_quincena():
    ingresos = [_make_ingreso("4000000", 50)]
    assert calcular_ingreso_quincena(ingresos, 2) == Decimal("2000000.00")


def test_calcular_dos_ingresos():
    ingresos = [
        _make_ingreso("4000000", 50),   # 2_000_000 por quincena
        _make_ingreso("1000000", 100),  # 1_000_000 en primera, 0 en segunda
    ]
    assert calcular_ingreso_quincena(ingresos, 1) == Decimal("3000000.00")
    assert calcular_ingreso_quincena(ingresos, 2) == Decimal("2000000.00")


def test_numero_quincena_invalido():
    import pytest
    with pytest.raises(ValueError):
        calcular_ingreso_quincena([], 3)


# --- fechas_quincena ---

def test_primera_quincena_enero():
    inicio, fin = fechas_quincena(2025, 1, 1)
    assert inicio == date(2025, 1, 1)
    assert fin == date(2025, 1, 15)


def test_segunda_quincena_enero():
    inicio, fin = fechas_quincena(2025, 1, 2)
    assert inicio == date(2025, 1, 16)
    assert fin == date(2025, 1, 31)


def test_segunda_quincena_febrero_bisiesto():
    inicio, fin = fechas_quincena(2024, 2, 2)
    assert fin == date(2024, 2, 29)


def test_segunda_quincena_febrero_no_bisiesto():
    inicio, fin = fechas_quincena(2025, 2, 2)
    assert fin == date(2025, 2, 28)


# --- total_ingresos_mensuales ---

def test_total_ingresos_mensuales():
    ingresos = [_make_ingreso("4000000"), _make_ingreso("1500000")]
    assert total_ingresos_mensuales(ingresos) == Decimal("5500000")
