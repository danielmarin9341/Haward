from decimal import Decimal

from django.db import migrations

# Imágenes que ya están en media/productos/ para el catálogo inicial.
# Antes dependían de db.sqlite3 (que ya no se versiona), por eso se vuelven a enlazar aquí.
IMAGENES = {
    "GeForce RTX 4070 SUPER 12GB": "productos/GeForce_RTX_4070_SUPER_12GB.png",
    "Radeon RX 7800 XT 16GB": "productos/Radeon_RX_7800_XT_16GB.png",
    "Corsair Vengeance 32GB DDR5": "productos/Corsair_Vengeance_32GB_DDR5.png",
    "Kingston Fury Beast 16GB DDR4": "productos/Kingston_Fury_Beast_16GB_DDR4.png",
    "ASUS TUF B650-PLUS WiFi": "productos/ASUS_TUF_B650-PLUS_WiFi.png",
    "NZXT H5 Flow RGB": "productos/NZXT_H5_Flow_RGB.png",
    "Logitech G Pro X Superlight": "productos/Logitech_G_Pro_X_Superlight.png",
    "Razer BlackWidow V3 Tenkeyless": "productos/Razer_BlackWidow_V3_Tenkeyless.png",
    "HyperX Cloud III": "productos/HyperX_Cloud_III.png",
    "AOC 27G2ZNE 27 pulgadas": "productos/AOC_27G2ZNE_27_pulgadas.png",
    "SSD NVMe Kingston NV2 1TB": "productos/SSD_NVMe_Kingston_NV2_1TB.png",
    "Fuente Corsair RM750e 750W": "productos/Fuente_Corsair_RM750e_750W.png",
}

# (nombre, categoría, marca, referencia, descripción, precio, cantidad, precio_oferta)
# Los precios son de ejemplo: ajústalos desde /admin/ según tu inventario real.
NUEVOS = [
    ("Intel Core i5-14600K", "Procesadores", "Intel", "i5-14600K · LGA1700", "14 núcleos · Socket LGA1700 · Desbloqueado para overclock", "1099000", 7, None),
    ("Intel Core i7-14700K", "Procesadores", "Intel", "i7-14700K · LGA1700", "20 núcleos · Socket LGA1700 · Alto rendimiento en juegos y creación", "1599000", 5, "1499000"),
    ("AMD Ryzen 5 7600", "Procesadores", "AMD", "Ryzen 5 7600 · AM5", "6 núcleos · Socket AM5 · Excelente relación precio-rendimiento", "799000", 10, None),
    ("AMD Ryzen 9 7950X", "Procesadores", "AMD", "Ryzen 9 7950X · AM5", "16 núcleos · Socket AM5 · Para estaciones de trabajo y streaming", "2199000", 3, None),
    ("GeForce RTX 4060 8GB", "Gráficas", "NVIDIA", "RTX 4060", "8 GB GDDR6 · DLSS 3 · Ideal para gaming en 1080p", "1499000", 9, "1399000"),
    ("Radeon RX 7600 8GB", "Gráficas", "AMD", "RX 7600", "8 GB GDDR6 · Gaming fluido en 1080p", "1099000", 8, None),
    ("MSI MAG B650 Tomahawk WiFi", "Boards", "MSI", "MAG B650 Tomahawk WiFi", "Socket AM5 · DDR5 · WiFi 6E", "1199000", 5, None),
    ("Gigabyte B760 Aorus Elite", "Boards", "Gigabyte", "B760 Aorus Elite", "Socket LGA1700 · DDR5 · Para procesadores Intel", "899000", 6, None),
    ("Kingston Fury Beast 32GB DDR5", "Memoria RAM", "Kingston", "2×16 GB · 5600 MHz", "Kit de memoria DDR5 con perfil XMP", "499000", 12, None),
    ("Corsair Vengeance LPX 16GB DDR4", "Memoria RAM", "Corsair", "2×8 GB · 3200 MHz", "Kit DDR4 de perfil bajo", "219000", 14, None),
    ("SSD NVMe Samsung 980 Pro 1TB", "Almacenamiento", "Samsung", "980 Pro · 1 TB", "SSD M.2 NVMe PCIe 4.0 de alto rendimiento", "459000", 8, None),
    ("SSD NVMe WD Blue SN580 500GB", "Almacenamiento", "Western Digital", "SN580 · 500 GB", "SSD M.2 NVMe PCIe 4.0 para uso diario", "229000", 13, None),
    ("Disco duro Seagate Barracuda 2TB", "Almacenamiento", "Seagate", "Barracuda · 2 TB", "Disco duro de 3.5 pulgadas · 7200 RPM", "319000", 10, None),
    ("Fuente Cooler Master MWE 650 Bronze", "Fuentes de poder", "Cooler Master", "MWE 650 · 650 W", "Fuente 80 PLUS Bronze para equipos de gama media", "329000", 9, None),
    ("Fuente MSI MAG A850GL 850W", "Fuentes de poder", "MSI", "MAG A850GL · 850 W", "Fuente modular 80 PLUS Gold compatible con PCIe 5", "599000", 4, None),
    ("Cooler Master MasterBox TD500 Mesh", "Gabinetes", "Cooler Master", "MasterBox TD500 Mesh", "Torre media · Frontal en malla · Ventiladores ARGB", "449000", 6, None),
    ("Corsair 4000D Airflow", "Gabinetes", "Corsair", "4000D Airflow", "Torre media · Panel de vidrio templado · Gran flujo de aire", "459000", 5, None),
    ("Logitech G435 Lightspeed", "Audífonos", "Logitech", "G435", "Inalámbricos · Ligeros · Bluetooth y Lightspeed", "229000", 12, None),
    ("Razer BlackShark V2 X", "Audífonos", "Razer", "BlackShark V2 X", "Sonido envolvente 7.1 · Micrófono cardioide", "249000", 8, "219000"),
    ("Razer DeathAdder V3", "Mouse", "Razer", "DeathAdder V3", "Ergonómico · Ultraligero · Sensor óptico de alta precisión", "329000", 9, None),
    ("Redragon Cobra M711", "Mouse", "Redragon", "Cobra M711", "Mouse gamer RGB · Hasta 10000 DPI", "79000", 20, None),
    ("Redragon Kumara K552", "Teclados", "Redragon", "Kumara K552", "Teclado mecánico compacto · Switches rojos · Retroiluminado", "139000", 15, None),
    ("HyperX Alloy Origins 60", "Teclados", "HyperX", "Alloy Origins 60", "Teclado mecánico 60% · Chasis de aluminio · RGB", "399000", 7, None),
    ("Samsung Odyssey G3 24 pulgadas", "Monitores", "Samsung", "Odyssey G3 · 24\"", "Full HD · 144 Hz · 1 ms · Panel VA", "699000", 6, None),
    ("Gigabyte G27F 2 27 pulgadas", "Monitores", "Gigabyte", "G27F 2 · 27\"", "Full HD · 165 Hz · 1 ms · Panel IPS", "749000", 5, "679000"),
    ("LG UltraGear 27GP850 27 pulgadas", "Monitores", "LG", "27GP850 · 27\"", "QHD · 165 Hz · Nano IPS · 1 ms", "1299000", 4, None),
]


def actualizar_catalogo(apps, schema_editor):
    Producto = apps.get_model("inventario", "Producto")

    for nombre, ruta in IMAGENES.items():
        for producto in Producto.objects.filter(nombre=nombre):
            if not producto.imagen:
                producto.imagen = ruta
                producto.save(update_fields=["imagen"])

    existentes = set(Producto.objects.values_list("nombre", flat=True))
    nuevos = []
    for nombre, categoria, marca, referencia, descripcion, precio, cantidad, oferta in NUEVOS:
        if nombre in existentes:
            continue
        nuevos.append(Producto(
            nombre=nombre, categoria=categoria, marca=marca, referencia=referencia,
            descripcion=descripcion, precio=Decimal(precio), cantidad=cantidad,
            en_oferta=oferta is not None,
            precio_oferta=Decimal(oferta) if oferta is not None else None,
        ))
    Producto.objects.bulk_create(nuevos)


class Migration(migrations.Migration):
    dependencies = [("inventario", "0007_pedidos")]

    operations = [migrations.RunPython(actualizar_catalogo, migrations.RunPython.noop)]
