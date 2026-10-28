from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    nombre = models.CharField("nombre", max_length=120)
    categoria = models.CharField("categoría", max_length=80, blank=True)
    marca = models.CharField("marca", max_length=80, blank=True)
    referencia = models.CharField("referencia", max_length=100, blank=True)
    imagen_url = models.URLField("URL de imagen", blank=True)
    cantidad = models.PositiveIntegerField("cantidad", default=0)
    precio = models.DecimalField(
        "precio unitario", max_digits=12, decimal_places=2,
        default=0, validators=[MinValueValidator(0)],
    )
    descripcion = models.TextField("descripción", blank=True)
    creado = models.DateTimeField("fecha de registro", auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre
