# FLEX-OP — Demo gratis en internet (Vercel + Render + SQLite)

Guía paso a paso para publicar la app como demo **sin pagar**, usando:

| Pieza | Servicio | Costo |
|-------|----------|-------|
| Frontend (Next.js) | [Vercel](https://vercel.com) | Gratis |
| Backend (Django) | [Render](https://render.com) | Gratis |
| Base de datos | SQLite (incluida en el backend) | Gratis |

> **Tiempo estimado:** 30–45 minutos la primera vez.  
> **Resultado:** una URL pública que puedes compartir para que otros entren y prueben la app.

---

## Antes de empezar

### Necesitas

1. **Cuenta de GitHub** — [github.com](https://github.com)
2. **Cuenta de Render** — [render.com](https://render.com) (registro con GitHub)
3. **Cuenta de Vercel** — [vercel.com](https://vercel.com) (registro con GitHub)
4. El código de este proyecto subido a un repositorio de GitHub

### Limitaciones del plan gratis (importante)

- **Render se duerme** tras ~15 minutos sin visitas. La primera persona que entre esperará **30–90 segundos** mientras despierta.
- El disco de Render es **efímero**: si redeployas, la base SQLite se borra y se vuelve a cargar el seed demo automáticamente.
- SQLite con **1 worker** (ya configurado): válido para demo; no para producción seria con muchos usuarios escribiendo a la vez.
- El seed en modo `demo` (~12 operarios, ~21 días de historial) tarda **1–3 minutos** en el **primer despliegue**.

---

## Parte 0 — Subir el código a GitHub

Si el repo ya está en GitHub, salta al [Parte 1](#parte-1--desplegar-el-backend-en-render).

### 0.1 Crear repositorio en GitHub

1. Entra a GitHub → **New repository**
2. Nombre ejemplo: `flexop-demo`
3. Público o privado (ambos funcionan)
4. **Create repository**

### 0.2 Subir el proyecto desde tu PC

En la terminal, dentro de la carpeta del proyecto:

```bash
cd /ruta/a/ProyectoWorkT

git init
git add .
git commit -m "Preparar demo FLEX-OP para Vercel + Render"

git branch -M main
git remote add origin https://github.com/TU_USUARIO/flexop-demo.git
git push -u origin main
```

Sustituye `TU_USUARIO/flexop-demo` por tu repo real.

---

## Parte 1 — Desplegar el backend en Render

### 1.1 Crear el servicio web

1. Entra a [dashboard.render.com](https://dashboard.render.com)
2. Clic en **New +** → **Web Service**
3. Conecta tu cuenta de GitHub si aún no lo hiciste
4. Busca y selecciona el repositorio `flexop-demo` (o como lo hayas llamado)
5. Clic en **Connect**

### 1.2 Configuración del servicio

Rellena **exactamente** así:

| Campo | Valor |
|-------|-------|
| **Name** | `flexop-api` (o el que quieras; anota la URL final) |
| **Region** | El más cercano a tus usuarios (ej. Oregon) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `chmod +x render-build.sh && ./render-build.sh` |
| **Start Command** | `chmod +x render-start.sh && ./render-start.sh` |
| **Instance Type** | **Free** |

### 1.3 Variables de entorno (Environment)

En la misma pantalla (o después en **Environment**), añade estas variables:

| Key | Value | Notas |
|-----|-------|-------|
| `DEBUG` | `False` | Obligatorio en producción |
| `SECRET_KEY` | *(ver abajo)* | Clave secreta única |
| `ALLOWED_HOSTS` | `flexop-api.onrender.com` | Cambia por **tu** subdominio de Render |
| `CORS_ALLOWED_ORIGINS` | `https://placeholder.vercel.app` | Lo actualizas en la Parte 4 |
| `POPULATE_SCALE` | `demo` | Dataset más liviano para arranque rápido |
| `SERVE_MEDIA` | `1` | Sirve archivos subidos |

**No añadas `DATABASE_URL`** — sin esa variable Django usa SQLite automáticamente.

#### Generar `SECRET_KEY`

En tu terminal:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copia el resultado y pégalo como valor de `SECRET_KEY`.

#### Cómo saber tu `ALLOWED_HOSTS`

Render te asigna una URL como:

`https://flexop-api.onrender.com`

El valor de `ALLOWED_HOSTS` es **solo el dominio**, sin `https://`:

```
flexop-api.onrender.com
```

### 1.4 Health check (opcional pero recomendado)

En **Settings** → **Health Check Path**:

```
/api/health/
```

### 1.5 Desplegar

1. Clic en **Create Web Service**
2. Render empezará a construir (build). Verás logs en tiempo real.
3. El **primer deploy** puede tardar **5–10 minutos** (instala dependencias + migraciones + seed demo).
4. Cuando termine, verás **Live** en verde.

### 1.6 Probar que el API responde

Abre en el navegador (cambia el dominio por el tuyo):

```
https://flexop-api.onrender.com/api/health/
```

Deberías ver:

```json
{"status": "ok", "service": "flexop-api"}
```

Si ves eso, el backend está listo.

---

## Parte 2 — Desplegar el frontend en Vercel

### 2.1 Importar el proyecto

1. Entra a [vercel.com/new](https://vercel.com/new)
2. **Import Git Repository** → selecciona el mismo repo de GitHub
3. Clic en **Import**

### 2.2 Configurar el proyecto

| Campo | Valor |
|-------|-------|
| **Project Name** | `flexop-demo` (o el que prefieras) |
| **Framework Preset** | Next.js (debería detectarlo solo) |
| **Root Directory** | Clic en **Edit** → escribe `flexop-frontend` → **Continue** |

### 2.3 Variable de entorno

En **Environment Variables**, añade:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://flexop-api.onrender.com/api` |

⚠️ Usa **tu** URL de Render, con `/api` al final, **sin** barra extra al final de `/api`.

Ejemplo correcto:

```
https://flexop-api.onrender.com/api
```

### 2.4 Desplegar

1. Clic en **Deploy**
2. Espera 2–5 minutos (build de Next.js)
3. Al terminar, Vercel te da una URL como:

```
https://flexop-demo.vercel.app
```

Abre esa URL: deberías ver la pantalla de **login** de FLEX-OP.

---

## Parte 3 — Conectar frontend y backend (CORS)

El frontend está en `*.vercel.app` y el API en `*.onrender.com`. Django debe permitir peticiones desde Vercel.

### 3.1 Actualizar CORS en Render

1. Vuelve a [dashboard.render.com](https://dashboard.render.com)
2. Abre el servicio `flexop-api`
3. Menú **Environment**
4. Edita `CORS_ALLOWED_ORIGINS` y pon la URL **exacta** de Vercel (con `https://`):

```
https://flexop-demo.vercel.app
```

Si Vercel te dio otra URL, usa esa. Sin barra final.

5. **Save Changes** — Render redeployará solo (2–3 min).

### 3.2 Probar login

1. Abre tu URL de Vercel
2. Si la página tarda en cargar datos, espera: Render puede estar despertando
3. Inicia sesión con:

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `admin` | `admin123` | Administrador |
| `supervisor1` | `super123` | Supervisor |
| `gerente1` | `gerente123` | Gerente |
| `operario1` | `operario123` | Operario |

Si el login funciona y ves el dashboard, **la demo está publicada**.

---

## Parte 4 — Compartir la demo

Envía a tus usuarios:

1. **URL:** `https://tu-app.vercel.app`
2. **Usuarios de prueba** (tabla de arriba)
3. **Nota:** la primera visita del día puede tardar ~1 minuto mientras Render despierta

---

## Archivos que prepara este repo para el deploy

| Archivo | Para qué sirve |
|---------|----------------|
| `backend/render-build.sh` | Build en Render (pip + collectstatic) |
| `backend/render-start.sh` | Migrate + seed SQLite + Gunicorn |
| `backend/runtime.txt` | Versión de Python |
| `backend/.env.render.example` | Plantilla de variables |
| `flexop-frontend/.env.example` | URL del API para Vercel |
| `flexop-frontend/vercel.json` | Config mínima de Vercel |
| `render.yaml` | Blueprint opcional de Render |

### Seed de datos: `full` vs `demo`

| Variable | Uso |
|----------|-----|
| `POPULATE_SCALE=demo` | Deploy gratis (más rápido) |
| `POPULATE_SCALE=full` | Local / servidor con más recursos |

Para forzar recarga de datos en Render, añade temporalmente `POPULATE_RESET=1`, guarda, espera el deploy, y luego quítala.

---

## Solución de problemas

### Error: `DisallowedHost`

- Revisa que `ALLOWED_HOSTS` en Render sea exactamente tu dominio `*.onrender.com` (sin `https://`).

### Error de CORS en el navegador (consola F12)

- `CORS_ALLOWED_ORIGINS` debe ser la URL exacta de Vercel, con `https://`.
- Tras cambiarla, espera a que Render termine el redeploy.

### Login falla / "Network Error"

1. Prueba `https://TU-API.onrender.com/api/health/` — si no responde, Render está dormido o el deploy falló.
2. Revisa que `NEXT_PUBLIC_API_URL` en Vercel termine en `/api`.
3. En Vercel → **Deployments** → los últimos deploys deben estar en verde.

### El deploy de Render falla en el build

- Revisa los **logs** en Render.
- Confirma **Root Directory** = `backend`.
- Confirma **Build Command** = `chmod +x render-build.sh && ./render-build.sh`

### El deploy tarda mucho en "Starting..."

- Normal en el **primer** arranque: migrate + `populate_db` con datos demo.
- Revisa logs: deberías ver `==> Cargando datos demo`.

### Los datos desaparecieron después de un redeploy

- En plan gratis el disco es efímero. El script vuelve a cargar demo si la DB está vacía.
- Para reset manual: `POPULATE_RESET=1` en Environment de Render.

### Quiero más datos en la demo online

Cambia en Render:

```
POPULATE_SCALE=full
```

El próximo deploy con DB vacía tardará más (~5–10 min en el arranque).

---

## Alternativa: Blueprint de Render

Si prefieres importar `render.yaml`:

1. Render → **New +** → **Blueprint**
2. Conecta el repo
3. Edita en el YAML las URLs de `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` antes de aplicar

La guía manual de arriba suele ser más clara la primera vez.

---

## Checklist final

- [ ] Repo en GitHub
- [ ] Render: servicio live, `/api/health/` responde OK
- [ ] Vercel: root `flexop-frontend`, `NEXT_PUBLIC_API_URL` configurada
- [ ] CORS en Render apunta a la URL de Vercel
- [ ] Login con `operario1` / `operario123` funciona

¡Listo para compartir tu demo de FLEX-OP!
