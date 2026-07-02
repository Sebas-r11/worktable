# Capítulo 17 — Recomendaciones

[← Índice](./README.md) | [← Anterior](./16-conclusiones.md) | [Siguiente →](./18-manual-tecnico.md)

---

## Recomendaciones técnicas

| Prioridad | Recomendación | Motivo (evidencia en código) |
|-----------|---------------|------------------------------|
| Alta | Implementar cookies **httpOnly** o BFF con sesión servidor | Tokens JWT accesibles por JavaScript |
| Alta | Completar UI para reglas de alerta y objetivos | Endpoints existen sin interfaz |
| Alta | Migrar `STATICFILES_STORAGE` a `STORAGES` (Django 5+) | Warning deprecación en tests |
| Media | Eliminar dependencias no usadas (celery, redis, reportlab) o implementarlas | `requirements.txt` vs imports |
| Media | Implementar generación PDF real o quitar formato PDF del modelo | `FormatoChoices.PDF` sin reportlab |
| Media | Corregir `objetivo_dia` hardcodeado en dashboard operario | Valor fijo 1000 en view |
| Media | Agregar endpoint `por_turno` o quitar de documentación ViewSet | Docstring sin `@action` |
| Media | Nginx delante para `/media/` en producción a escala | `SERVE_MEDIA` es solución básica |
| Baja | Implementar página Perfil en TopBar | Ítem sin handler |
| Baja | Badge sugerencias pendientes con total global | Solo cuenta página actual |
| Baja | Server-side auth en Next.js middleware | Protección actual solo cliente |
| Baja | Completar `tests.py` stubs en apps | Archivos vacíos en raíz apps |

## Recomendaciones académicas (ADSO)

1. **Anexar al informe escrito** los diagramas Mermaid exportados como imágenes para Word.
2. **Incluir capturas de pantalla** siguiendo la guía del Capítulo 19.
3. **Documentar en memoria escrita** la justificación organizacional que no está en el repositorio.
4. **Registrar evidencia de ejecución CI** (badge o captura pipeline GitHub Actions).
5. **Realizar prueba de aceptación con usuarios** por rol usando credenciales demo.

## Recomendaciones de despliegue

1. Configurar `SECRET_KEY`, `POSTGRES_PASSWORD` y `ALLOWED_HOSTS` en `.env` antes de prod.
2. Mantener `RUN_POPULATE=0` en producción salvo primer despliegue controlado.
3. Ejecutar `collectstatic` vía entrypoint (ya automatizado).
4. Considerar HTTPS con certificado en proxy inverso.

Ver también: [Anexo — Deuda técnica](./anexo-deuda-tecnica.md).
