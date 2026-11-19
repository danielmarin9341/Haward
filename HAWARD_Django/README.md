# Inventario de hardware

Aplicación web básica para registrar y consultar productos de una tienda de hardware. Usa Django y SQLite; `src/Main.java` permite iniciar el servidor local desde IntelliJ.

## Requisitos

- Python 3.10 o posterior
- Java 17 o posterior (solo para iniciar desde `Main.java`)

## Iniciar con Python

Desde la carpeta raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_DEBUG = "1"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre <http://127.0.0.1:8000/>. Crear, editar y eliminar productos requiere iniciar sesión con un usuario del personal (`/admin/`).

## Variables de entorno (producción)

- `DJANGO_SECRET_KEY`: obligatoria cuando `DJANGO_DEBUG` no es `1`.
- `DJANGO_DEBUG`: solo `1` en desarrollo local; por defecto está apagado.
- `DATABASE_URL`: URL de PostgreSQL. Sin ella se usa SQLite, que en Render se borra en cada despliegue.

Pruebas: `python manage.py test`. Para iniciar desde IntelliJ, ejecuta `src/Main.java` después de instalar las dependencias y aplicar las migraciones.

## Funciones

- Listar y buscar productos por nombre, categoría, marca o referencia.
- Agregar, editar y eliminar productos.
- Ver el total de referencias y unidades disponibles.
- Administrar productos también desde `/admin/` después de crear un superusuario con `python manage.py createsuperuser`.

La base de datos local `db.sqlite3` se crea al ejecutar las migraciones y no se sube a GitHub (está en `.gitignore`).
