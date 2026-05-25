# 🏛️ Reporte de Control Arquitectónico Intermedio

> Documento generado mediante la skill `/improve-codebase-architecture` tras completar los issues #001 y #007 del sprint inicial. Registra el diagnóstico, las tres propuestas de interfaz evaluadas y la solución híbrida implementada.

---

## 1. Diagnóstico Inicial del Repositorio

**Fecha de revisión:** 2026-05-24  
**Issues completados al momento:** #001 (Auth), #007 (Ingresos mensuales)  
**Herramienta:** Claude Code — skill `/improve-codebase-architecture`

### Hallazgos del análisis libre del repositorio

Claude exploró el repositorio buscando módulos superficiales, lógica dispersa y dependencias cíclicas. Estos fueron los hallazgos:

#### 🔴 Problema 1 — Lógica de negocio mezclada con la capa de API
**Archivo afectado:** `backend/app/api/quincenas.py`  
El helper `calcular_fechas(anio, mes, numero)` vive dentro del archivo del router. Esta función es lógica de dominio pura (no depende de FastAPI) y debería vivir en `services/`. Si en el futuro se necesita calcular fechas desde otro módulo (por ejemplo, al crear recordatorios automáticos), habría que importar desde el router, creando un acoplamiento invertido.

#### 🟡 Problema 2 — Modelo `Base` acoplado a `user.py`
**Archivo afectado:** `backend/app/models/user.py`  
La clase `Base = DeclarativeBase()` está definida dentro de `user.py`. Todos los demás modelos importan `Base` desde ahí, lo que crea una dependencia implícita: si `user.py` cambia su estructura, puede romper las importaciones de `quincena.py`, `gasto.py` y `deuda.py`. Es un acoplamiento innecesario.

#### 🟡 Problema 3 — Helper duplicado entre routers
**Archivos afectados:** `backend/app/api/gastos.py` y `backend/app/api/deudas.py`  
La función `get_quincena_del_usuario(db, quincena_id, user)` está copiada en ambos archivos. Si la lógica de verificación de ownership cambia (por ejemplo, agregar roles o permisos), hay que modificar dos lugares. Violación del principio DRY.

#### 🟢 Oportunidad 1 — Sin dependencias cíclicas detectadas
Los modelos no se importan entre sí de forma circular. Las relaciones SQLAlchemy usan strings (`"Quincena"`, `"User"`) para evitar imports directos.

#### 🟢 Oportunidad 2 — Servicios correctamente aislados
`auth_service.py` e `ingreso_service.py` son funciones puras sin dependencias de FastAPI. Esto es una fortaleza que debe mantenerse en todos los servicios futuros.

---

## 2. Candidatos de Profundización Identificados

Tras el diagnóstico, Claude presentó la siguiente lista numerada de candidatos para profundización arquitectónica:

| # | Módulo | Problema | Riesgo para siguientes issues |
|---|--------|----------|-------------------------------|
| 1 | Lógica de fechas en `quincenas.py` | Acoplamiento router-dominio | Alto — issues #002, #003 y #005 necesitan calcular fechas |
| 2 | `Base` en `user.py` | Acoplamiento implícito entre modelos | Medio — riesgo al agregar nuevos modelos en #002 |
| 3 | Helper duplicado en `gastos.py` / `deudas.py` | Violación DRY | Medio — se agravará al agregar permisos en issues futuros |

**Decisión del equipo:** Se priorizó el **Candidato #1** (lógica de fechas) por tener el mayor riesgo para los issues inmediatos del sprint, y el **Candidato #2** (Base aislada) por ser un cambio de bajo costo y alto impacto.

---

## 3. Tres Propuestas de Interfaz (Simulación Multi-Agente)

Claude simuló tres sub-agentes con enfoques radicalmente distintos para resolver los problemas identificados:

---

### 🤖 Sub-agente A — "Separación Estricta por Capas"

**Filosofía:** Cada capa tiene una responsabilidad única y no puede importar de capas superiores.

**Propuesta para lógica de fechas:**
```python
# backend/app/domain/quincena_domain.py  ← nueva capa "domain"
from datetime import date
import calendar

class QuincenaDomain:
    @staticmethod
    def calcular_fechas(anio: int, mes: int, numero: int) -> tuple[date, date]:
        if numero == 1:
            return date(anio, mes, 1), date(anio, mes, 15)
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        return date(anio, mes, 16), date(anio, mes, ultimo_dia)
    
    @staticmethod
    def validar_numero(numero: int) -> bool:
        return numero in (1, 2)
```

**Propuesta para Base:**
```python
# backend/app/db/base.py  ← Base separada de los modelos
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

**Ventajas:** Máxima separación, fácil de testear, escalable.  
**Desventajas:** Introduce una capa nueva (`domain/`) que puede ser excesiva para un MVP. Más archivos, más complejidad de navegación.

---

### 🤖 Sub-agente B — "Services como único punto de verdad"

**Filosofía:** No crear capas nuevas. Mover toda la lógica de dominio a `services/` y hacer los routers lo más delgados posible.

**Propuesta para lógica de fechas:**
```python
# backend/app/services/quincena_service.py  ← servicio nuevo
from datetime import date
import calendar
from sqlalchemy.orm import Session
from app.models.quincena import Quincena
from app.models.user import User

def calcular_fechas(anio: int, mes: int, numero: int) -> tuple[date, date]:
    if numero == 1:
        return date(anio, mes, 1), date(anio, mes, 15)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, 16), date(anio, mes, ultimo_dia)

def get_quincena_del_usuario(db: Session, quincena_id, user: User) -> Quincena:
    """Helper centralizado — elimina la duplicación en gastos y deudas."""
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id,
        Quincena.user_id == user.id
    ).first()
    return q
```

**Propuesta para Base:**
```python
# backend/app/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
# Todos los modelos importan Base desde aquí, no desde user.py
```

**Ventajas:** Consistente con la arquitectura existente. No introduce capas nuevas. Resuelve los 3 problemas identificados.  
**Desventajas:** `services/` puede crecer demasiado si no se modera.

---

### 🤖 Sub-agente C — "Módulo de utilidades compartidas"

**Filosofía:** Crear un módulo `utils/` para lógica transversal que no pertenece a ningún dominio específico.

**Propuesta para lógica de fechas:**
```python
# backend/app/utils/fecha_utils.py
from datetime import date
import calendar

def calcular_fechas_quincena(anio: int, mes: int, numero: int) -> tuple[date, date]:
    if numero == 1:
        return date(anio, mes, 1), date(anio, mes, 15)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, 16), date(anio, mes, ultimo_dia)

# backend/app/utils/db_utils.py
def get_or_404(db, model, filters: dict, detail: str = "No encontrado"):
    obj = db.query(model).filter_by(**filters).first()
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj
```

**Ventajas:** Separa utilidades genéricas de lógica de dominio. Muy reutilizable.  
**Desventajas:** `utils/` suele convertirse en un cajón de sastre. Dificulta encontrar lógica de negocio específica.

---

## 4. Evaluación y Solución Híbrida Implementada

### Decisión del equipo

Tras evaluar las tres propuestas, se eligió una **solución híbrida basada en el Sub-agente B** con elementos del Sub-agente A:

| Problema | Solución elegida | Justificación |
|----------|-----------------|---------------|
| Lógica de fechas en router | Mover a `services/quincena_service.py` (Sub-agente B) | Consistente con arquitectura existente. Sin capas nuevas. |
| `Base` en `user.py` | Mover a `db/base.py` (Sub-agente A y B coinciden) | Cambio de bajo costo, elimina acoplamiento implícito. |
| Helper duplicado | Centralizar en `quincena_service.py` (Sub-agente B) | Un solo lugar para lógica de ownership. |

### Cambios implementados

**1. Nuevo archivo `backend/app/db/base.py`:**
```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```
Todos los modelos (`user.py`, `quincena.py`, `gasto.py`, `deuda.py`) ahora importan `Base` desde `app.db.base`.

**2. Nuevo archivo `backend/app/services/quincena_service.py`:**
```python
import calendar
from datetime import date
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.quincena import Quincena
from app.models.user import User

def calcular_fechas(anio: int, mes: int, numero: int) -> tuple[date, date]:
    if numero == 1:
        return date(anio, mes, 1), date(anio, mes, 15)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, 16), date(anio, mes, ultimo_dia)

def get_quincena_del_usuario(db: Session, quincena_id: UUID, user: User) -> Quincena:
    q = db.query(Quincena).filter(
        Quincena.id == quincena_id,
        Quincena.user_id == user.id
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quincena no encontrada")
    return q
```

**3. Routers actualizados** para importar desde `quincena_service` en lugar de definir lógica localmente.

### Verificación post-refactor

Tras aplicar los cambios:
- ✅ `pytest backend/tests/` — todos los tests en verde
- ✅ Sin imports circulares detectados
- ✅ `uvicorn app.main:app --reload` levanta sin errores
- ✅ `GET /auth/me`, `POST /quincenas/`, `GET /gastos/quincena/{id}` responden correctamente

---

## 5. Próximos Puntos de Control

| Tras completar | Revisar |
|----------------|---------|
| Issues #003 y #004 | Verificar que `gastos.py` y `deudas.py` usan `quincena_service.get_quincena_del_usuario` |
| Issue #005 | Verificar que `recordatorio_service` sigue siendo función pura sin imports de FastAPI |
| Issue #006 (frontend) | Auditar que no hay lógica de negocio en componentes React — toda la lógica en hooks o servicios JS |

---

*Reporte generado con Claude Code — skill `/improve-codebase-architecture`*
