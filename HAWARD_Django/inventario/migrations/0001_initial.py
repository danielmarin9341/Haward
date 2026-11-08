import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Producto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, verbose_name="nombre")),
                ("categoria", models.CharField(blank=True, max_length=80, verbose_name="categoría")),
                ("marca", models.CharField(blank=True, max_length=80, verbose_name="marca")),
                ("referencia", models.CharField(blank=True, max_length=100, verbose_name="referencia")),
                ("cantidad", models.PositiveIntegerField(default=0, verbose_name="cantidad")),
                ("precio", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name="precio unitario")),
                ("descripcion", models.TextField(blank=True, verbose_name="descripción")),
                ("creado", models.DateTimeField(auto_now_add=True, verbose_name="fecha de registro")),
            ],
            options={"verbose_name": "producto", "verbose_name_plural": "productos", "ordering": ["nombre"]},
        ),
    ]
