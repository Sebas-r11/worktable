# Cómo correr FLEX-OP

## Backend (Django)

```bash
# Desde la raíz del proyecto
cd /home/sebastian/Escritorio/ProyectoWorkT

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# Aplicar migraciones (solo la primera vez o tras cambios)
python manage.py migrate

# Cargar datos de prueba (opcional)
python populate_db.py

# Correr servidor
python manage.py runserver
```

El backend corre en: **http://localhost:8000**  
Admin de Django: **http://localhost:8000/admin**  
Swagger API: **http://localhost:8000/swagger**

---

## Frontend (Next.js)

```bash
# En otra terminal
cd /home/sebastian/Escritorio/ProyectoWorkT/flexop-frontend

# Instalar dependencias (solo la primera vez)
npm install

# Correr servidor de desarrollo
npm run dev
```

El frontend corre en: **http://localhost:3000**

---

## Usuarios de prueba

Revisar `populate_db.py` para ver los usuarios y contraseñas cargados.

---

## Resumen: dos terminales en paralelo

| Terminal 1 (backend)            | Terminal 2 (frontend)                      |
|---------------------------------|--------------------------------------------|
| `source .venv/bin/activate`     | `cd flexop-frontend`                       |
| `python manage.py runserver`    | `npm run dev`                              |
