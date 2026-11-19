import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0006_producto_en_oferta_producto_precio_oferta"),
    ]

    operations = [
        migrations.CreateModel(
            name="Pedido",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="código")),
                ("nombre", models.CharField(max_length=120, verbose_name="nombre completo")),
                ("email", models.EmailField(max_length=254, verbose_name="correo electrónico")),
                ("telefono", models.CharField(max_length=20, verbose_name="teléfono")),
                ("direccion", models.CharField(max_length=200, verbose_name="dirección de entrega")),
                ("ciudad", models.CharField(max_length=80, verbose_name="ciudad")),
                ("notas", models.TextField(blank=True, verbose_name="notas para el pedido")),
                (
                    "metodo_pago",
                    models.CharField(
                        choices=[
                            ("contra_entrega", "Pago contra entrega"),
                            ("transferencia", "Transferencia bancaria / Nequi"),
                        ],
                        default="contra_entrega",
                        max_length=20,
                        verbose_name="método de pago",
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("pendiente", "Pendiente de pago"),
                            ("pagado", "Pagado"),
                            ("enviado", "Enviado"),
                            ("entregado", "Entregado"),
                            ("cancelado", "Cancelado"),
                        ],
                        default="pendiente",
                        max_length=12,
                        verbose_name="estado",
                    ),
                ),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="subtotal")),
                ("envio", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="envío")),
                ("total", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="total")),
                ("creado", models.DateTimeField(auto_now_add=True, verbose_name="fecha del pedido")),
            ],
            options={
                "verbose_name": "pedido",
                "verbose_name_plural": "pedidos",
                "ordering": ["-creado"],
            },
        ),
        migrations.CreateModel(
            name="PedidoItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, verbose_name="producto")),
                ("precio_unitario", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="precio unitario")),
                ("cantidad", models.PositiveIntegerField(verbose_name="cantidad")),
                (
                    "pedido",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="inventario.pedido",
                    ),
                ),
                (
                    "producto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="inventario.producto",
                    ),
                ),
            ],
            options={
                "verbose_name": "producto del pedido",
                "verbose_name_plural": "productos del pedido",
            },
        ),
    ]
