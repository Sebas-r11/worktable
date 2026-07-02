# Capítulo 8 — Arquitectura del sistema

[← Índice](./README.md) | [← Anterior](./07-requerimientos.md) | [Siguiente →](./09-tecnologias.md)

---

## Arquitectura general

**Patrón:** Cliente-Servidor en **3 capas** con API REST como frontera.

```mermaid
flowchart TB
  subgraph presentacion [Capa de presentación]
    UI[Next.js 16 - React 19]
    RQ[React Query]
    ZS[Zustand Auth]
  end
  subgraph aplicacion [Capa de aplicación]
    DRF[Django REST Framework]
    PERM[Permissions + Mixins]
    SVC[Lógica en Models / Views]
  end
  subgraph datos [Capa de datos]
    ORM[Django ORM]
    PG[(PostgreSQL)]
    FS[Media / Static]
  end
  UI --> RQ
  RQ -->|HTTP /api JWT| DRF
  ZS --> UI
  DRF --> PERM
  PERM --> SVC
  SVC --> ORM
  ORM --> PG
  SVC --> FS
```

## Componentes principales

| Componente | Tecnología | Responsabilidad |
|------------|------------|-----------------|
| Cliente web | Next.js App Router | UI, routing, proxy API |
| Cliente HTTP | Axios + interceptors | JWT, refresh automático |
| Estado servidor | TanStack React Query | Cache, polling, mutaciones |
| API | Django + DRF | CRUD, acciones, validación |
| Auth | SimpleJWT + blacklist | Tokens access/refresh |
| Persistencia | PostgreSQL / SQLite | Datos transaccionales |
| Archivos | FileField/ImageField | Logos, reportes, perfiles |
| Estáticos prod | WhiteNoise | CSS/JS admin y DRF |
| Contenedores | Docker Compose | Orquestación local/prod |
| CI | GitHub Actions | Verificación automática |

## Flujo de información

```mermaid
sequenceDiagram
  participant U as Usuario
  participant F as Next.js
  participant A as Django API
  participant D as PostgreSQL
  U->>F: Acción en UI
  F->>A: HTTP + Bearer JWT
  A->>A: Permisos + tenant filter
  A->>D: ORM query/mutation
  D-->>A: Resultado
  A-->>F: JSON paginado
  F-->>U: Actualización UI
```

### Flujo de autenticación

```mermaid
sequenceDiagram
  participant U as Usuario
  participant F as Frontend
  participant A as API
  U->>F: username + password
  F->>A: POST /auth/login/
  A-->>F: access + refresh
  F->>F: Cookies flexop_access/refresh
  F->>A: GET /usuarios/me/
  A-->>F: User + rol + empresa
  F->>F: Redirect por rol
```

## Patrones de diseño utilizados

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **MVC / MVT (Django)** | Models, Views, URLs | Separación backend |
| **Repository-like (Querysets)** | `*/querysets.py` | Optimización de consultas |
| **Mixin** | `EmpresaFilterMixin`, `EmpresaPerformCreateMixin` | Cross-cutting tenant |
| **ViewSet + Router** | Todas las apps | REST uniforme |
| **Custom actions** | `@action` en ViewSets | Operaciones de negocio |
| **SPA + BFF proxy** | `middleware.ts` | Unificar origen `/api` |
| **Observer-like (polling)** | React Query `refetchInterval` | Actualización periódica |
| **State management** | Zustand persist | Sesión de usuario |

**No evidenciado en código:** microservicios, event-driven (Celery sin usar), CQRS, GraphQL.
