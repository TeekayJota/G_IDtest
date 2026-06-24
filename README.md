# GamerID · Beyond the Dreams

Plataforma de inscripción a torneos de eSports. Implementación fiel del prototipo
`GamerID Prototipo.dc.html` con backend real en **Django**.

- **Público (sin cuenta):** inicio, listado de torneos, detalle, formulario de
  inscripción (los campos cambian según el torneo) y confirmación con código de
  seguimiento.
- **Staff (con login y roles):** bandeja de inscripciones con filtros y búsqueda,
  detalle con aprobar / rechazar / poner en revisión, notas internas y línea de
  estado, y creación de torneos (solo Admin).

Torneos **gratuitos** (sin pagos). Avisos por correo **configurados pero apagados**.

## Stack

- Django 5.1 (templates server-rendered)
- Base de datos: **SQLite** en desarrollo → **Postgres** en producción (un cambio en `.env`)
- Usuario propio con roles **Admin / Staff**

## Puesta en marcha

```bash
# 1. Activar el entorno virtual
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 2. (si es la primera vez) instalar dependencias
pip install -r requirements.txt

# 3. Migrar y cargar datos demo
python manage.py migrate
python manage.py seed_demo

# 4. Levantar el servidor
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

### Accesos de staff (datos demo)

| Rol   | Usuario             | Contraseña     |
|-------|---------------------|----------------|
| Admin | `admin`             | `gamerid2026`  |
| Admin | `carla@gamerid.gg`  | `gamerid2026`  |
| Staff | `luis@gamerid.gg`   | `gamerid2026`  |

- Panel de staff: `/staff/`
- Admin de Django (apoyo de super-admin): `/admin/`

> La barra superior **"PROTOTIPO · DEMO"** permite saltar entre pantallas. Se
> controla con `SHOW_DEMO_NAV` (encendida en desarrollo, apagada en producción).

## Pasar a Postgres

1. Crear la base y el usuario en tu Postgres.
2. En `.env` (copia `.env.example`):
   ```
   DATABASE_URL=postgres://usuario:password@localhost:5432/gamerid
   ```
3. `python manage.py migrate`. Nada más cambia.

## Activar correos

Cuando el cliente entregue su SMTP, completar `EMAIL_*` y `SEND_STATUS_EMAILS=True`
en `.env`. El aviso al jugador al cambiar de estado ya está implementado.

## Estructura

```
gamerid/        configuración (settings, urls, context processors)
accounts/       usuario con roles (Admin/Staff)
tournaments/    modelos, vistas, formularios, seed de datos demo
templates/      public/ · staff/ · partials/
static/         css/styles.css (design system) · js/app.js
```
