# 📋 Bitácora de Transferencia de Contexto (Handoffs)

> Este archivo registra los resúmenes de contexto generados mediante la skill `/handoff` al final de cada bloque de issues. Su propósito es inicializar limpias las siguientes sesiones del agente Ralph, evitando la degradación por acumulación de tokens.

---

## Handoff #1 — Fin del Sprint 1 (Issues 001 y 007)

**Fecha:** 2026-05-24  
**Issues completados:** `#001` Autenticación JWT · `#007` Ingresos mensuales  
**Branch:** `master`

### ✅ Componentes construidos

- **`backend/app/models/user.py`** — Modelo SQLAlchemy `User` con campos `id (UUID)`, `email`, `hashed_password`, `created_at`. Relaciones definidas con `Quincena`.
- **`backend/app/models/quincena.py`** — Modelo `Quincena` con campos `anio`, `mes`, `numero`, `fecha_inicio`, `fecha_fin`, `ingresos`. Restricción de unicidad por `(user_id, anio, mes, numero)`.
- **`backend/app/models/gasto.py`** — Modelo `Gasto` con enum `CategoriaGasto` (arriendo, alimentacion, servicios, transporte, salud, educacion, entretenimiento, otro).
- **`backend/app/models/deuda.py`** — Modelo `Deuda` con enum `EstadoDeuda` (pendiente, pagada) y campo `fecha_vencimiento`.
- **`backend/app/services/auth_service.py`** — Funciones puras: `hash_password`, `verify_password`, `create_access_token`, `decode_token`, `authenticate_user`. JWT con expiración de 7 días.
- **`backend/app/services/ingreso_service.py`** — Funciones: `ingreso_primera_quincena`, `ingreso_segunda_quincena`, `calcular_ingreso_quincena`, `fechas_quincena`, `total_ingresos_mensuales`.
- **`backend/app/api/auth.py`** — Endpoints: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`. Dependencia `get_current_user` reutilizable.
- **`backend/tests/test_auth.py`** — 6 tests: registro exitoso, email duplicado, login correcto, login incorrecto, `/me` con token, `/me` sin token. Todos en verde ✅
- **`backend/tests/test_ingreso_service.py`** — 13 tests cubriendo distribución quincenales, febrero bisiesto, múltiples fuentes. Todos en verde ✅

### 🏗️ Decisiones de arquitectura consolidadas

1. **Base declarativa única:** `Base = DeclarativeBase()` vive en `models/user.py` y todos los demás modelos importan desde allí. Evita conflictos de metadatos con Alembic.
2. **Servicios como funciones puras:** `auth_service` e `ingreso_service` no importan FastAPI ni dependen del request cycle. Son testeables sin levantar la app.
3. **UUID como PK:** Todos los modelos usan `UUID(as_uuid=True)` de PostgreSQL. Evita colisiones y facilita la distribución futura.
4. **Soft delete en ingresos:** El campo `activo: bool` permite desactivar ingresos sin borrar el historial de quincenas anteriores.
5. **JWT stateless:** No hay tabla de sesiones. El token se valida con la clave secreta en cada request.

### ⏳ Pendiente exacto para el siguiente sprint

- Issues `#002` (quincenas CRUD), `#003` (gastos API), `#004` (deudas API) están **desbloqueados** — dependen solo de `#001` que ya está completo.
- Issue `#005` (recordatorios) bloqueado hasta que `#004` esté completo.
- Issue `#006` (frontend dashboard) bloqueado hasta que `#003`, `#004` y `#005` estén completos.
- **No hay migrations de Alembic aún** — pendiente crear `alembic.ini` y la carpeta `alembic/versions/`.
- **No hay `conftest.py` con fixtures de base de datos SQLite** para los tests de integración de los endpoints.

### 🚫 Reglas que el agente debe respetar en el siguiente ciclo

- No crear lógica de negocio dentro de los routers de FastAPI. Toda lógica va en `services/`.
- No usar `db.query()` directamente en los endpoints — usar funciones del servicio correspondiente.
- Mantener los tests como "vertical slices": un test nuevo por funcionalidad antes de implementar.
- Commits en formato: `feat(#NNN): descripción` o `test(#NNN): descripción`.

---

## Handoff #2 — Fin del Sprint 2 (Issues 002, 003 y 004)

**Fecha:** 2026-05-24  
**Issues completados:** `#002` Quincenas CRUD · `#003` API Gastos · `#004` API Deudas  
**Branch:** `master`

### ✅ Componentes construidos

- **`backend/app/api/quincenas.py`** — CRUD completo: `POST /quincenas`, `GET /quincenas`, `GET /quincenas/{id}`, `PATCH /quincenas/{id}`, `DELETE /quincenas/{id}`. Validación de duplicados y fechas automáticas.
- **`backend/app/api/gastos.py`** — Endpoints: crear, listar, resumen por categoría, actualizar, eliminar. Validación de monto > 0.
- **`backend/app/api/deudas.py`** — Endpoints: crear, listar por quincena, listar pendientes, recordatorios, actualizar estado, eliminar.
- **`backend/app/services/recordatorio_service.py`** — Función `clasificar_urgencia(fecha_vencimiento, hoy)` retorna `urgente | proximo | a_tiempo`. Función `get_recordatorios(db, user)` retorna lista ordenada con días restantes.
- **`backend/tests/conftest.py`** — Fixtures: base de datos SQLite en memoria, cliente de test, `usuario_token`, `auth_headers`. Aislamiento total entre tests.
- **`backend/tests/test_gastos.py`** — 5 tests incluyendo aislamiento entre usuarios.
- **`backend/tests/test_deudas.py`** — 5 tests incluyendo marcar como pagada y aislamiento.

### 🏗️ Decisiones de arquitectura consolidadas

1. **Helper `get_quincena_del_usuario`** compartido en `gastos.py` y `deudas.py` — evita duplicar la lógica de verificación de ownership.
2. **Recordatorios como endpoint en `deudas.py`** — no se creó un router separado para evitar proliferación de archivos pequeños.
3. **SQLite para tests** — `conftest.py` usa `sqlite:///./test.db` con `create_all/drop_all` por fixture. No requiere PostgreSQL corriendo en CI.

### ⏳ Pendiente exacto para el siguiente sprint

- Issue `#005` (recordatorios avanzados) — parcialmente implementado en `recordatorio_service.py`, falta endpoint dedicado con filtros.
- Issue `#006` (frontend) — completamente bloqueado, es el siguiente gran bloque.
- Falta crear `backend/.env.example` con las variables requeridas.
- Falta configurar Alembic para migraciones reales contra PostgreSQL.

### 🚫 Reglas para el siguiente ciclo

- El frontend debe consumir exclusivamente la API REST. No compartir lógica de negocio entre frontend y backend.
- Usar `fetch` nativo o `axios` en React — no usar librerías de state management hasta que el MVP funcione.
- Todos los componentes React deben ser funcionales con hooks. No usar class components.

---
