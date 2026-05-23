# [feature] 007 — Gestión de ingresos mensuales y distribución quincenales

## Contexto

El usuario puede tener uno o varios ingresos mensuales (salario, freelance, negocio propio, etc.). La app debe permitir registrarlos y distribuirlos automáticamente entre las dos quincenas del mes, según el porcentaje que el usuario configure.

Por ejemplo: si alguien gana $4.000.000 de salario y le pagan el 15 y el 30, puede configurar 50%/50%. Si le pagan todo el 30, configura 0%/100%.

## Trabajo por hacer

**Endpoints de ingresos mensuales:**

- `POST /ingresos` — crea una fuente de ingreso mensual.
- `GET /ingresos` — lista los ingresos activos del usuario.
- `PATCH /ingresos/{id}` — actualiza monto, nombre o porcentaje.
- `DELETE /ingresos/{id}` — desactiva un ingreso (soft delete con `activo=False`).

**Integración con quincenas:**

- `GET /quincenas/{anio}/{mes}/{numero}/ingreso-esperado` — calcula y retorna el ingreso esperado para esa quincena sumando todos los ingresos activos del usuario según su distribución.
- Al crear una quincena, pre-llenar el campo `ingresos` con el ingreso esperado calculado (el usuario puede ajustarlo manualmente si el monto real fue diferente).

## Modelo de datos

```python
class IngresoMensual(Base):
    id: UUID
    user_id: UUID
    nombre: str           # "Salario Empresa ABC", "Freelance diseño"
    tipo: TipoIngreso     # salario | freelance | negocio | arriendo_recibido | pension | otro
    monto_mensual: Decimal
    porcentaje_primera_quincena: int   # 0-100; segunda = 100 - este valor
    activo: bool          # False = desactivado sin borrar historial
    created_at: datetime
```

## Lógica de negocio

- `porcentaje_primera_quincena` debe estar entre 0 y 100.
- La suma de ambas quincenas siempre da el `monto_mensual` exacto.
- Si el usuario ajusta manualmente el campo `ingresos` de una quincena, ese valor toma precedencia sobre el calculado.
- El campo `disponible` de la quincena = `ingresos (real o esperado) - gastos - deudas pendientes`.

## Criterios de aceptación

- [ ] `porcentaje_primera_quincena` fuera del rango 0-100 retorna 422.
- [ ] `monto_mensual` ≤ 0 retorna 422.
- [ ] El ingreso esperado de primera + segunda quincena suma exactamente el `monto_mensual`.
- [ ] Desactivar un ingreso no borra el historial de quincenas anteriores.
- [ ] Un usuario no puede ver ni modificar los ingresos de otro usuario.
- [ ] Tests cubriendo los casos anteriores.

## Tipo

`[feature]` — depende del issue 001 (auth). Es independiente de los issues 002-006.
