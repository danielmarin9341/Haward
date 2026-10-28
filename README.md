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
python manage.py migrate
python manage.py runserver
```

Abre <http://127.0.0.1:8000/>. Para iniciar desde IntelliJ, ejecuta `src/Main.java` después de instalar las dependencias y aplicar las migraciones.

## Funciones

- Listar y buscar productos por nombre, categoría, marca o referencia.
- Agregar, editar y eliminar productos.
- Ver el total de referencias y unidades disponibles.
- Administrar productos también desde `/admin/` después de crear un superusuario con `python manage.py createsuperuser`.

La base de datos local `db.sqlite3` se crea al ejecutar las migraciones y no se sube a GitHub.
