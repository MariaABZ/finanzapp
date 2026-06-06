from decimal import Decimal
from datetime import date
from app.services.ingreso_service import ingreso_primera_quincena, ingreso_segunda_quincena, fechas_quincena, calcular_ingreso_quincena
from app.services.recordatorio_service import clasificar_urgencia

def test_primera_quincena_50():
    assert ingreso_primera_quincena(Decimal("4000000"), 50) == Decimal("2000000.00")

def test_suma_quincenas_igual_mensual():
    m, p = Decimal("4000000"), 60
    assert ingreso_primera_quincena(m, p) + ingreso_segunda_quincena(m, p) == m

def test_fechas_primera_quincena():
    inicio, fin = fechas_quincena(2025, 6, 1)
    assert inicio == date(2025, 6, 1) and fin == date(2025, 6, 15)

def test_fechas_segunda_quincena_bisiesto():
    _, fin = fechas_quincena(2024, 2, 2)
    assert fin == date(2024, 2, 29)

def test_urgencia_vencida():
    assert clasificar_urgencia(date(2025, 6, 1), date(2025, 6, 10)) == "urgente"

def test_urgencia_proximo():
    assert clasificar_urgencia(date(2025, 6, 12), date(2025, 6, 10)) == "proximo"

def test_urgencia_a_tiempo():
    assert clasificar_urgencia(date(2025, 6, 17), date(2025, 6, 10)) == "a_tiempo"

def test_register(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "secret123"})
    assert r.status_code == 201

def test_login(client):
    client.post("/auth/register", json={"email": "x@b.com", "password": "pass1234"})
    r = client.post("/auth/login", json={"email": "x@b.com", "password": "pass1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_crear_quincena(client, auth_headers):
    r = client.post("/quincenas/", json={"anio": 2025, "mes": 6, "numero": 1}, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["fecha_inicio"] == "2025-06-01"

def test_crear_gasto(client, auth_headers):
    r = client.post("/quincenas/", json={"anio": 2025, "mes": 8, "numero": 1}, headers=auth_headers)
    qid = r.json()["id"]
    r2 = client.post("/gastos", json={"quincena_id": qid, "categoria": "alimentacion", "descripcion": "Mercado", "monto": "150000"}, headers=auth_headers)
    assert r2.status_code == 201

def test_crear_deuda(client, auth_headers):
    r = client.post("/quincenas/", json={"anio": 2025, "mes": 8, "numero": 2}, headers=auth_headers)
    qid = r.json()["id"]
    r2 = client.post("/deudas", json={"quincena_id": qid, "entidad": "Bancolombia", "descripcion": "Cuota", "monto": "300000", "fecha_vencimiento": "2025-08-14"}, headers=auth_headers)
    assert r2.status_code == 201

def test_crear_ingreso(client, auth_headers):
    r = client.post("/ingresos/", json={"nombre": "Salario", "tipo": "salario", "monto_mensual": "4000000"}, headers=auth_headers)
    assert r.status_code == 201
