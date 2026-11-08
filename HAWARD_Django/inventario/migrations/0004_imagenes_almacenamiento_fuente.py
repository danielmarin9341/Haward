from django.db import migrations


IMAGENES = {
    "SSD NVMe Kingston NV2 1TB": "https://media.kingston.com/kingston/product/SNV2S_1000GB_tn.png",
    "Fuente Corsair RM750e 750W": "https://assets.corsair.com/image/upload/c_pad%2Cq_85%2Ch_1100%2Cw_1100%2Cf_auto/v1680721027/products/Power-Supply-Units/base-rme-series-psu-config/CP-9020248/Gallery/RM750e_01.webp",
}


def asignar_imagenes(apps, schema_editor):
    Producto = apps.get_model("inventario", "Producto")
    for nombre, url in IMAGENES.items():
        Producto.objects.filter(nombre=nombre, imagen_url="").update(imagen_url=url)


class Migration(migrations.Migration):
    dependencies = [("inventario", "0003_producto_imagen_url")]

    operations = [migrations.RunPython(asignar_imagenes, migrations.RunPython.noop)]
