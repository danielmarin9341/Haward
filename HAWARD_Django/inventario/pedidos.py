"""Lógica del carrito y de la creación de pedidos (el precio y el stock siempre se validan en el servidor)."""
import json
from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import Pedido, PedidoItem, Producto

ENVIO_GRATIS_DESDE = Decimal("500000")
COSTO_ENVIO = Decimal("15000")
MAX_LINEAS = 50
MAX_UNIDADES_POR_LINEA = 99


class CarritoError(Exception):
    """El carrito no es válido o no se puede completar la compra."""


def parsear_carrito(texto):
    """Convierte el JSON {"id": cantidad} enviado por el navegador en {int: int}."""
    try:
        datos = json.loads(texto or "{}")
    except ValueError:
        raise CarritoError("No se pudo leer tu carrito. Vuelve a la tienda e inténtalo de nuevo.")
    if not isinstance(datos, dict) or not datos:
        raise CarritoError("Tu carrito está vacío.")
    if len(datos) > MAX_LINEAS:
        raise CarritoError("Tu carrito tiene demasiados productos distintos.")

    carrito = {}
    for clave, cantidad in datos.items():
        try:
            producto_id = int(clave)
        except (TypeError, ValueError):
            raise CarritoError("Tu carrito contiene un producto no válido.")
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise CarritoError("Tu carrito contiene una cantidad no válida.")
        if cantidad < 1 or cantidad > MAX_UNIDADES_POR_LINEA:
            raise CarritoError("Tu carrito contiene una cantidad no válida.")
        carrito[producto_id] = cantidad
    return carrito


def costo_envio(subtotal):
    return Decimal("0") if subtotal >= ENVIO_GRATIS_DESDE else COSTO_ENVIO


@transaction.atomic
def crear_pedido(datos_cliente, carrito):
    """Crea el pedido y descuenta el stock. Lanza CarritoError si algo no se puede vender."""
    productos = {
        p.pk: p for p in Producto.objects.select_for_update().filter(pk__in=carrito.keys())
    }
    if len(productos) != len(carrito):
        raise CarritoError("Alguno de los productos de tu carrito ya no está disponible.")

    lineas = []
    subtotal = Decimal("0")
    for producto_id, cantidad in carrito.items():
        producto = productos[producto_id]
        if producto.cantidad < cantidad:
            if producto.cantidad == 0:
                raise CarritoError(f"«{producto.nombre}» está agotado.")
            raise CarritoError(
                f"Solo quedan {producto.cantidad} unidades de «{producto.nombre}». "
                "Ajusta la cantidad en tu carrito."
            )
        precio = producto.precio_vigente
        subtotal += precio * cantidad
        lineas.append((producto, precio, cantidad))

    envio = costo_envio(subtotal)
    pedido = Pedido.objects.create(
        **datos_cliente, subtotal=subtotal, envio=envio, total=subtotal + envio,
    )
    PedidoItem.objects.bulk_create(
        PedidoItem(
            pedido=pedido, producto=producto, nombre=producto.nombre,
            precio_unitario=precio, cantidad=cantidad,
        )
        for producto, precio, cantidad in lineas
    )
    for producto, _precio, cantidad in lineas:
        Producto.objects.filter(pk=producto.pk).update(cantidad=F("cantidad") - cantidad)
    return pedido
