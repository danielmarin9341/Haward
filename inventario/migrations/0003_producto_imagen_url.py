from django.db import migrations, models


IMAGENES = {
    "GeForce RTX 4070 SUPER 12GB": "https://images.unsplash.com/photo-1621164071312-67bb68821b3f?auto=format&fit=crop&w=800&q=80",
    "Radeon RX 7800 XT 16GB": "https://images.unsplash.com/photo-1727895949000-da3c10a7d562?auto=format&fit=crop&w=800&q=80",
    "AMD Ryzen 7 7800X3D": "https://image.itmedia.co.jp/pcuser/articles/2304/05/l_si7101-X3D-01.jpg",
    "Corsair Vengeance 32GB DDR5": "https://images.unsplash.com/photo-1676554565685-3aeb5d7ad1b7?auto=format&fit=crop&w=800&q=80",
    "Kingston Fury Beast 16GB DDR4": "https://images.unsplash.com/photo-1669480380756-f82b044e8144?auto=format&fit=crop&w=800&q=80",
    "ASUS TUF B650-PLUS WiFi": "https://images.unsplash.com/photo-1687071523279-93ec8e5e53b7?auto=format&fit=crop&w=800&q=80",
    "NZXT H5 Flow RGB": "https://nzxt.com/cdn/shop/files/h5-flow-hero-white_d2c463a3-4488-4ce4-af26-5efe234814ed.png?v=1762528066",
    "Logitech G Pro X Superlight": "https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=800&q=80",
    "Razer BlackWidow V3 Tenkeyless": "https://assets3.razerzone.com/m7OuMTVAYSmQCAEfKZF3xi-BpRw%3D/1500x1000/https%3A%2F%2Fmedias-p1.phoenix.razer.com%2Fsys-master-phoenix-images-container%2Fh07%2Fha3%2F9533909860382%2Fblackwidow-v3-tkl-4-500x500.png",
    "HyperX Cloud III": "https://br-media.hptiendaenlinea.com/catalog/product/cache/74c1057f7991b4edb2bc7bdaa94de933/7/2/727A8AA-2_T1731516660.png",
    "AOC 27G2ZNE 27 pulgadas": "https://cdn.sanity.io/images/hf5b3axp/production/83385cfd7b948a58b7e3b06ac0c5677c07f9dd21-3840x3840.png?auto=format&fit=max&w=1200",
}


def asignar_imagenes(apps, schema_editor):
    Producto = apps.get_model("inventario", "Producto")
    for nombre, url in IMAGENES.items():
        Producto.objects.filter(nombre=nombre, imagen_url="").update(imagen_url=url)


class Migration(migrations.Migration):
    dependencies = [("inventario", "0002_catalogo_inicial")]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="imagen_url",
            field=models.URLField(blank=True, verbose_name="URL de imagen"),
        ),
        migrations.RunPython(asignar_imagenes, migrations.RunPython.noop),
    ]
