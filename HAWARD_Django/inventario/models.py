import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    nombre = models.CharField("nombre", max_length=120)
    categoria = models.CharField("categoría", max_length=80, blank=True)
    marca = models.CharField("marca", max_length=80, blank=True)
    referencia = models.CharField("referencia", max_length=100, blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    cantidad = models.PositiveIntegerField("cantidad", default=0)
    precio = models.DecimalField(
        "precio unitario", max_digits=12, decimal_places=2,
        default=0, validators=[MinValueValidator(0)],
    )
    en_oferta = models.BooleanField("en promoción", default=False)
    precio_oferta = models.DecimalField(
        "precio de oferta", max_digits=12, decimal_places=2,
        blank=True, null=True, validators=[MinValueValidator(0)],
    )
    descripcion = models.TextField("descripción", blank=True)
    creado = models.DateTimeField("fecha de registro", auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre

    @property
    def precio_vigente(self):
        """Precio que paga el cliente: el de oferta si el producto está en promoción."""
        if self.en_oferta and self.precio_oferta is not None:
            return self.precio_oferta
        return self.precio


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de pago"
        PAGADO = "pagado", "Pagado"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    class MetodoPago(models.TextChoices):
        CONTRA_ENTREGA = "contra_entrega", "Pago contra entrega"
        TRANSFERENCIA = "transferencia", "Transferencia bancaria / Nequi"

    # Código público e imposible de adivinar para consultar el pedido
    codigo = models.UUIDField("código", default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField("nombre completo", max_length=120)
    email = models.EmailField("correo electrónico")
    telefono = models.CharField("teléfono", max_length=20)
    direccion = models.CharField("dirección de entrega", max_length=200)
    ciudad = models.CharField("ciudad", max_length=80)
    notas = models.TextField("notas para el pedido", blank=True)
    metodo_pago = models.CharField(
        "método de pago", max_length=20,
        choices=MetodoPago.choices, default=MetodoPago.CONTRA_ENTREGA,
    )
    estado = models.CharField(
        "estado", max_length=12,
        choices=Estado.choices, default=Estado.PENDIENTE,
    )
    subtotal = models.DecimalField("subtotal", max_digits=12, decimal_places=2)
    envio = models.DecimalField("envío", max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField("total", max_digits=12, decimal_places=2)
    creado = models.DateTimeField("fecha del pedido", auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido {self.referencia} · {self.nombre}"

    @property
    def referencia(self):
        """Referencia corta para mostrar al cliente (primeros 8 caracteres del código)."""
        return str(self.codigo).split("-")[0].upper()


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(
        Producto, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
    )
    # Se guardan nombre y precio del momento de la compra, por si el producto cambia o se borra
    nombre = models.CharField("producto", max_length=120)
    precio_unitario = models.DecimalField("precio unitario", max_digits=12, decimal_places=2)
    cantidad = models.PositiveIntegerField("cantidad")

    class Meta:
        verbose_name = "producto del pedido"
        verbose_name_plural = "productos del pedido"

    def __str__(self):
        return f"{self.cantidad} × {self.nombre}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
