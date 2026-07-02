# Capítulo 8 — Datos de demostración

[← Índice](./README.md) | [← Anterior](./07-roles-permisos.md) | [Siguiente: Comandos →](./09-comandos-desarrollo.md)

---

Tras `populate_db.py` (automático en Docker dev si la DB está vacía):

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | ADMIN |
| `supervisor1` | `super123` | SUPERVISOR |
| `gerente1` | `gerente123` | GERENTE |
| `operario1` | `operario123` | OPERARIO |

Empresa demo: **ACME Manufacturing** (RUC `20123456789`).

Regenerar datos operativos:

```bash
docker compose exec backend env POPULATE_RESET=1 python populate_db.py
```
