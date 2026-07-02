# Capítulo 3 — Arquitectura del sistema

[← Índice](./README.md) | [← Anterior](./02-estructura-repositorio.md) | [Siguiente: Backend →](./04-backend.md)

---

```mermaid
flowchart LR
  subgraph cliente [Cliente]
    Browser[Navegador]
  end
  subgraph frontend [flexop-frontend :3000]
    Next[Next.js App Router]
    Proxy[middleware /api/*]
  end
  subgraph backend [backend :8000]
    DRF[Django REST Framework]
    JWT[JWT SimpleJWT]
    Apps[8 apps Django]
  end
  subgraph data [Datos]
  PG[(PostgreSQL)]
  Media[/media uploads/]
  Static[/static WhiteNoise/]
  end
  Browser --> Next
  Next --> Proxy
  Proxy --> DRF
  DRF --> JWT
  DRF --> Apps
  Apps --> PG
  DRF --> Media
  DRF --> Static
```

## Autenticación y autorización

- **Backend:** JWT (`rest_framework_simplejwt`) con refresh token, rotación y blacklist.
- **Frontend:** tokens en cookies (`flexop_access`, `flexop_refresh`); interceptor Axios renueva en 401.
- **Roles:** `OPERARIO`, `SUPERVISOR`, `GERENTE`, `ADMIN`.
- **Multitenancy:** mixin `EmpresaFilterMixin` filtra querysets por empresa del usuario; validación cruzada en serializers (`tenant_validation.py`).
- **Permisos:** módulo `usuarios/permissions.py` (`IsSupervisorOrAbove`, etc.).

## Paginación

- API: `PageNumberPagination`, **20 registros por página**.
- Frontend: componente `PaginationBar` en todos los listados principales.
