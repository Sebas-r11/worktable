# Capítulo 11 — Calidad y mejoras conocidas

[← Índice](./README.md) | [← Anterior](./10-flujo-operativo.md) | [Siguiente: Referencias →](./12-referencias.md)

---

| Área | Estado |
|------|--------|
| Tests backend | ~139 tests pytest |
| Tests frontend | Vitest + MSW + Playwright e2e |
| Auditoría P0–P2 | Implementada (concurrencia, N+1, paginación, descarga segura) |
| Infra prod (#29) | WhiteNoise, collectstatic, SERVE_MEDIA |
| `STATICFILES_STORAGE` | Deprecation warning Django 5.1 → migrar a `STORAGES` |
| Media a escala | Recomendado nginx/object storage en prod grande |
| Badge pendientes sugerencias | Cuenta solo página actual, no total global |
