# 💰 FinanzApp

> Aplicación web de gestión financiera personal quincenales — controla deudas, gastos y recordatorios de pago en un solo lugar.

![Estado del proyecto](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/backend-FastAPI%20%2B%20Python-009688)
![React](https://img.shields.io/badge/frontend-React%20%2B%20TypeScript-61DAFB)
![Licencia](https://img.shields.io/badge/licencia-MIT-blue)

---

## 📋 Tabla de contenidos

- [Descripción](#descripción)
- [Características principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Instalación y configuración](#instalación-y-configuración)
- [Uso](#uso)
- [Flujo de trabajo con Claude Code](#flujo-de-trabajo-con-claude-code)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Issues y roadmap](#issues-y-roadmap)
- [Contribuir](#contribuir)

---

## Descripción

FinanzApp es una aplicación web full-stack que permite a los usuarios gestionar sus finanzas personales por quincena. El objetivo es simple: saber exactamente cuánto dinero entra, cuánto se va en gastos fijos, qué deudas hay pendientes y cuándo hay que pagarlas — todo en una interfaz clara y sin fricciones.

**Problema que resuelve:** muchas personas pierden control de sus finanzas porque los gastos y deudas están dispersos en notas, mensajes de WhatsApp o simplemente en la memoria. FinanzApp centraliza todo en un panel quincenales con recordatorios automáticos.

---

## Características principales

- **Ingresos mensuales:** registro de fuentes de ingreso (salario, freelance, negocio) con distribución automática entre la primera y segunda quincena.
- **Panel quincenales:** resumen de ingresos esperados vs reales, gastos y deudas para cada quincena.
- **Gestión de deudas:** registro de deudas con entidad (banco o persona), monto, fecha de vencimiento y estado.
- **Gastos fijos:** categorías como arriendo, alimentación, servicios públicos y transporte con visualización de barras.
- **Recordatorios de pago:** alertas por proximidad de vencimiento (urgente, próximo, a tiempo).
- **Historial:** registro de quincenas anteriores para ver la evolución financiera.
- **Autenticación:** registro e inicio de sesión por usuario.

---

## Arquitectura

```
FinanzApp
├── Backend  →  FastAPI (Python) + PostgreSQL
└── Frontend →  React + TypeScript + TailwindCSS
```

**Backend (FastAPI):**
- API REST con endpoints para usuarios, quincenas, gastos y deudas.
- Base de datos PostgreSQL con SQLAlchemy como ORM.
- Autenticación JWT.
- Servicio de recordatorios con lógica de fechas por quincena.

**Frontend (React + TypeScript):**
- Panel principal con métricas por quincena.
- Formularios para agregar gastos y deudas.
- Visualización de barras de progreso por categoría.
- Sistema de alertas de recordatorios.

---

## Instalación y configuración

### Requisitos previos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # configura tus variables de entorno
alembic upgrade head            # ejecuta migraciones
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

La app estará disponible en `http://localhost:5173` y la API en `http://localhost:8000`.

---

## Uso

1. Registra tu usuario en `/register`.
2. En el panel principal, selecciona la quincena actual.
3. Agrega tus ingresos de la quincena.
4. Registra tus gastos fijos (arriendo, alimentación, servicios, transporte).
5. Añade tus deudas activas con fecha de vencimiento.
6. El sistema mostrará recordatorios automáticos según qué tan cerca está cada vencimiento.

---

## Flujo de trabajo con Claude Code

Este proyecto se desarrolla usando **Claude Code** como herramienta principal de desarrollo, siguiendo el flujo de trabajo AFK Agent descrito en [Running Your AFK Agent](https://www.aihero.dev/running-your-afk-agent-a9l1u).

### ¿Cómo funciona el flujo?

El flujo se basa en tres pilares:

**1. Issues como fuente de verdad**
Cada funcionalidad, bugfix o mejora se describe en un archivo Markdown dentro del directorio `issues/`. Cada issue tiene:
- Título claro y contexto suficiente
- Criterios de aceptación concretos
- Etiqueta de tipo: `[bugfix]`, `[infra]`, `[feature]`, `[polish]`, `[refactor]`

**2. El agente `ralph`**
El script `ralph/once.sh` ejecuta Claude Code en modo HITL (Human-In-The-Loop):
- Lee los issues abiertos en `issues/`
- Revisa los últimos 5 commits para entender el contexto
- Carga el prompt del agente desde `ralph/prompt.md`
- Le pasa todo a Claude con permiso para escribir y hacer commits

```bash
bash ralph/once.sh
```

**3. Desarrollo guiado por TDD**
El agente usa la skill `/tdd` para implementar cada feature:
- Primero escribe el test (vertical slice: un test, una implementación)
- Luego implementa el código mínimo para pasarlo
- Corre los feedback loops (`pytest`, `npm run typecheck`)
- Hace un commit descriptivo

### Priorización de tareas

El agente sigue este orden de prioridad, igual que el prompt del artículo:

1. 🐛 Bugfixes
2. 🏗️ Infraestructura y tests
3. ✨ Features (tracer bullets primero)
4. 💅 Polish y UX
5. ♻️ Refactors

### HITL vs AFK

- **HITL (Human-In-The-Loop):** el desarrollador observa al agente trabajar y puede intervenir. Ideal para tareas nuevas donde aún se están afinando los prompts y las descripciones de issues.
- **AFK (Away From Keyboard):** el agente trabaja de forma autónoma en issues etiquetados como `[afk]`. Se usa una vez que los prompts y la estructura del repositorio están bien establecidos.

---

## Estructura del proyecto

```
finanzapp/
├── README.md
├── .claude/
│   └── skills/
│       └── tdd/                  # Skill de TDD para el agente
│           ├── SKILL.md
│           ├── tests.md
│           └── mocking.md
├── ralph/
│   ├── prompt.md                 # Instrucciones del agente
│   └── once.sh                   # Script para ejecutar el agente
├── issues/
│   ├── 001-auth-usuario.md
│   ├── 002-modelo-quincena.md
│   ├── 003-api-gastos.md
│   ├── 004-api-deudas.md
│   ├── 005-recordatorios.md
│   ├── 006-frontend-dashboard.md
│   └── done/                     # Issues completados
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── quincena.py
│   │   │   ├── gasto.py
│   │   │   └── deuda.py
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── quincenas.py
│   │   │   ├── gastos.py
│   │   │   └── deudas.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       └── recordatorio_service.py
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_gastos.py
│       └── test_deudas.py
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── MetricCard.tsx
│       │   ├── DeudaItem.tsx
│       │   ├── GastoBar.tsx
│       │   └── RecordatorioItem.tsx
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Deudas.tsx
│       │   ├── Gastos.tsx
│       │   └── Login.tsx
│       ├── hooks/
│       │   ├── useQuincena.ts
│       │   └── useDeudas.ts
│       └── utils/
│           └── fecha.ts
└── docs/
    └── client-brief.md
```

---

## Issues y roadmap

| # | Issue | Tipo | Estado |
|---|-------|------|--------|
| 001 | Autenticación de usuarios (registro/login JWT) | `infra` | 🟡 En progreso |
| 002 | Modelo de quincena y endpoints CRUD | `feature` | ⚪ Pendiente |
| 003 | API de gastos por categoría | `feature` | ⚪ Pendiente |
| 004 | API de deudas con fecha de vencimiento | `feature` | ⚪ Pendiente |
| 005 | Servicio de recordatorios por proximidad | `feature` | ⚪ Pendiente |
| 006 | Frontend: dashboard quincenales | `feature` | ⚪ Pendiente |
| 007 | Ingresos mensuales con distribución quincenales | `feature` | ⚪ Pendiente |

---

## Contribuir

Este proyecto se desarrolla como proyecto universitario. Si quieres contribuir:

1. Haz fork del repositorio.
2. Crea un branch desde `main`: `git checkout -b feature/nombre-feature`.
3. Escribe tu issue en `issues/` siguiendo el formato existente.
4. Usa `bash ralph/once.sh` para ejecutar el agente en modo HITL.
5. Abre un Pull Request con descripción clara del cambio.

---

*Desarrollado con ❤️ usando Claude Code como herramienta principal de desarrollo.*
