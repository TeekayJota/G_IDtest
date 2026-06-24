# Despliegue de GamerID

## Railway (Postgres) — método elegido ⭐

Railway tiene **filesystem efímero**: SQLite no persiste ahí. Por eso usamos su
**Postgres gestionado** (1 clic, persistente). La app ya lo soporta vía
`DATABASE_URL`, así que **no se toca código**.

1. Sube el repo a **GitHub**.
2. En Railway: **New Project → Deploy from GitHub repo** → este repo.
3. **Add Postgres:** botón *New → Database → PostgreSQL* (en el mismo proyecto).
4. En el **servicio de la app → Variables**, define:

   ```
   DATABASE_URL   = ${{Postgres.DATABASE_URL}}
   SECRET_KEY     = (tu clave de .env.production.example)
   DEBUG          = False
   SHOW_DEMO_NAV  = False
   ADMIN_USERNAME = admin
   ADMIN_PASSWORD = (una contraseña fuerte)
   ADMIN_EMAIL    = tu@correo.com
   # Cuando confirmes HTTPS (Railway lo da por defecto en el dominio público):
   COOKIE_SECURE       = True
   SECURE_SSL_REDIRECT = True
   ```

   > No necesitas `ALLOWED_HOSTS`: la app agrega sola el dominio
   > `*.up.railway.app`. Para un **dominio propio**, añade
   > `ALLOWED_HOSTS=tudominio.com` y `CSRF_TRUSTED_ORIGINS=https://tudominio.com`.

5. **Deploy.** En cada deploy, `railway.json` ejecuta `migrate` y `ensure_admin`
   (crea tu administrador la primera vez). Nixpacks corre `collectstatic` en el build.
6. Entra a `https://<tu-app>.up.railway.app/staff/` con el admin creado y empieza
   a crear torneos desde el panel.
7. *(Opcional)* Datos demo: ejecuta una vez `python manage.py seed_demo` desde un
   comando one-off de Railway. ⚠️ **Borra datos** — no lo uses con inscripciones reales.

> Variables ≠ `.env`: en Railway las variables van en el **dashboard**, no en el
> archivo `.env` (que no se sube). El `.env` es solo para tu máquina local.

---

## Alternativa: VPS con SQLite + WhiteNoise

Pensado para un **VPS/servidor con disco persistente**, sin costos extra de
base de datos ni CDN. SQLite + WhiteNoise cubren el demo y los primeros eventos.

## Pasos en el servidor

```bash
# 1. Código + entorno
git clone <repo> gamerid && cd gamerid          # o copiar la carpeta
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Variables de entorno de producción
cp .env.production.example .env
#   editar .env -> poner tu dominio en ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS

# 3. Base de datos
python manage.py migrate

# 4. Estáticos (obligatorio con DEBUG=False; WhiteNoise los sirve)
python manage.py collectstatic --noinput

# 5. Primer usuario administrador (datos LIMPIOS, sin demo)
python manage.py createsuperuser        # crea tu admin real

# 6. Servir la app (detrás de Nginx/Caddy para HTTPS)
gunicorn gamerid.wsgi:application -b 0.0.0.0:8000     # Linux
# waitress-serve --port=8000 gamerid.wsgi:application  # Windows
```

> El admin creado con `createsuperuser` entra al panel en `/staff/`. Asígnale
> rol **Admin** desde `/admin/` (modelo Usuario) para que pueda crear torneos.

## ⚠️ Importante

- **NO ejecutes `seed_demo` en producción**: borra torneos e inscripciones y
  carga datos de prueba. Es solo para desarrollo/demo.
- **Disco persistente**: el archivo `db.sqlite3` es tu única fuente de datos.
  No uses plataformas de filesystem efímero (se borraría en cada deploy).
- **HTTPS**: cuando el dominio tenga certificado, activa en `.env`
  `SECURE_SSL_REDIRECT`, `COOKIE_SECURE` y `SECURE_HSTS_SECONDS`.

## Respaldos (hazlo, es tu único almacén)

Copia segura "en caliente" (no corrompe aunque la app esté escribiendo):

```bash
sqlite3 db.sqlite3 ".backup '/ruta/backups/gamerid-$(date +%F-%H%M).db'"
```

Prográmalo con cron (ej. diario) y antes de cada evento importante.

## Migrar a Postgres en el futuro (si hiciera falta)

1. Crear base y usuario en Postgres.
2. En `.env`: `DATABASE_URL=postgres://usuario:password@host:5432/gamerid`
3. `python manage.py migrate`. Nada más del código cambia.
