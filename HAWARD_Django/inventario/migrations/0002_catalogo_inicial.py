from decimal import Decimal

from django.db import migrations


PRODUCTOS_INICIALES = [
    {
        "nombre": "GeForce RTX 4070 SUPER 12GB",
        "categoria": "Gráficas",
        "marca": "NVIDIA",
        "referencia": "RTX 4070 SUPER",
        "descripcion": "12 GB GDDR6X · DLSS 3 · Ideal para gaming en 1440p",
        "precio": "3299000.00",
        "cantidad": 6,
    },
    {
        "nombre": "Radeon RX 7800 XT 16GB",
        "categoria": "Gráficas",
        "marca": "AMD",
        "referencia": "RX 7800 XT",
        "descripcion": "16 GB GDDR6 · Alto rendimiento en 1440p",
        "precio": "2799000.00",
        "cantidad": 4,
    },
    {
        "nombre": "AMD Ryzen 7 7800X3D",
        "categoria": "Procesadores",
        "marca": "AMD",
        "referencia": "7800X3D · AM5",
        "descripcion": "8 núcleos · Socket AM5 · Procesador para gaming",
        "precio": "1899000.00",
        "cantidad": 8,
    },
    {
        "nombre": "Corsair Vengeance 32GB DDR5",
        "categoria": "Memoria RAM",
        "marca": "Corsair",
        "referencia": "2×16 GB · 6000 MHz",
        "descripcion": "Memoria DDR5 de alto rendimiento",
        "precio": "549000.00",
        "cantidad": 12,
    },
    {
        "nombre": "Kingston Fury Beast 16GB DDR4",
        "categoria": "Memoria RAM",
        "marca": "Kingston",
        "referencia": "2×8 GB · 3200 MHz",
        "descripcion": "Kit de memoria DDR4 para equipos de escritorio",
        "precio": "229000.00",
        "cantidad": 15,
    },
    {
        "nombre": "ASUS TUF B650-PLUS WiFi",
        "categoria": "Boards",
        "marca": "ASUS",
        "referencia": "TUF B650-PLUS WiFi",
        "descripcion": "Socket AM5 · DDR5 · WiFi 6",
        "precio": "1099000.00",
        "cantidad": 5,
    },
    {
        "nombre": "NZXT H5 Flow RGB",
        "categoria": "Gabinetes",
        "marca": "NZXT",
        "referencia": "H5 Flow RGB",
        "descripcion": "Torre media · Panel lateral de vidrio · Flujo de aire optimizado",
        "precio": "599000.00",
        "cantidad": 3,
    },
    {
        "nombre": "Logitech G Pro X Superlight",
        "categoria": "Mouse",
        "marca": "Logitech",
        "referencia": "G Pro X Superlight",
        "descripcion": "Inalámbrico · Sensor HERO · Diseño ultraligero",
        "precio": "529000.00",
        "cantidad": 9,
    },
    {
        "nombre": "Razer BlackWidow V3 Tenkeyless",
        "categoria": "Teclados",
        "marca": "Razer",
        "referencia": "BlackWidow V3 TKL",
        "descripcion": "Teclado mecánico compacto · Switches amarillos",
        "precio": "419000.00",
        "cantidad": 6,
    },
    {
        "nombre": "HyperX Cloud III",
        "categoria": "Audífonos",
        "marca": "HyperX",
        "referencia": "Cloud III",
        "descripcion": "Audífonos over-ear · Sonido envolvente DTS · Micrófono removible",
        "precio": "389000.00",
        "cantidad": 10,
    },
    {
        "nombre": "AOC 27G2ZNE 27 pulgadas",
        "categoria": "Monitores",
        "marca": "AOC",
        "referencia": "27G2ZNE",
        "descripcion": "Full HD · 240 Hz · 1 ms · Adaptive Sync",
        "precio": "899000.00",
        "cantidad": 5,
    },
    {
        "nombre": "SSD NVMe Kingston NV2 1TB",
        "categoria": "Almacenamiento",
        "marca": "Kingston",
        "referencia": "NV2 · 1 TB",
        "descripcion": "Unidad SSD M.2 NVMe PCIe 4.0",
        "precio": "329000.00",
        "cantidad": 11,
    },
    {
        "nombre": "Fuente Corsair RM750e 750W",
        "categoria": "Fuentes de poder",
        "marca": "Corsair",
        "referencia": "RM750e · 750 W",
        "descripcion": "Fuente modular con certificación 80 PLUS Gold",
        "precio": "579000.00",
        "cantidad": 4,
    },
]


def agregar_productos(apps, schema_editor):
    Producto = apps.get_model("inventario", "Producto")
    existentes = set(Producto.objects.values_list("nombre", flat=True))
    nuevos = []
    for producto in PRODUCTOS_INICIALES:
        if producto["nombre"] in existentes:
            continue
        datos = producto.copy()
        datos["precio"] = Decimal(datos["precio"])
        nuevos.append(Producto(**datos))
    Producto.objects.bulk_create(nuevos)


class Migration(migrations.Migration):
    dependencies = [("inventario", "0001_initial")]

    operations = [migrations.RunPython(agregar_productos, migrations.RunPython.noop)]
