from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PedidoForm, ProductoForm
from .models import Pedido, Producto
from .pedidos import (
    COSTO_ENVIO, ENVIO_GRATIS_DESDE, CarritoError, crear_pedido, parsear_carrito,
)


def lista_productos(request):
    consulta = request.GET.get("q", "").strip()
    productos = Producto.objects.all()
    if consulta:
        productos = productos.filter(
            Q(nombre__icontains=consulta)
            | Q(categoria__icontains=consulta)
            | Q(marca__icontains=consulta)
            | Q(referencia__icontains=consulta)
        )
    datos_tienda = [
        {
            "id": producto.pk,
            "name": producto.nombre,
            "cat": producto.categoria or "Otros",
            "brand": producto.marca,
            "spec": producto.descripcion or producto.referencia or producto.marca or "Hardware",
            "price": float(producto.precio),
            "stock": producto.cantidad,
            "icon": (producto.marca or producto.nombre)[:18],
            "imagen": producto.imagen.url if producto.imagen else '',
            "is_on_sale": producto.en_oferta and producto.precio_oferta is not None,
            "sale_price": float(producto.precio_oferta) if producto.precio_oferta is not None else None,
        }
        for producto in productos
    ]
    contexto = {
        "productos_json": datos_tienda,
        "total_productos": Producto.objects.count(),
        "total_unidades": Producto.objects.aggregate(total=Sum("cantidad"))["total"] or 0,
        "envio_gratis_desde": ENVIO_GRATIS_DESDE,
    }
    return render(request, "inventario/lista.html", contexto)


@staff_member_required
def crear_producto(request):
    form = ProductoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto agregado al inventario.")
        return redirect("lista_productos")
    return render(request, "inventario/formulario.html", {"form": form, "titulo": "Agregar producto"})


@staff_member_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, request.FILES or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("lista_productos")
    return render(request, "inventario/formulario.html", {"form": form, "titulo": "Editar producto"})


@staff_member_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado del inventario.")
        return redirect("lista_productos")
    return render(request, "inventario/confirmar_eliminacion.html", {"producto": producto})


def checkout(request):
    """Pantalla de pago: datos de entrega, método de pago y resumen del carrito."""
    if request.method == "POST":
        form = PedidoForm(request.POST)
        carrito = None
        try:
            carrito = parsear_carrito(request.POST.get("carrito", ""))
        except CarritoError as error:
            form.add_error(None, str(error))
        if carrito is not None and form.is_valid():
            try:
                pedido = crear_pedido(form.cleaned_data, carrito)
            except CarritoError as error:
                form.add_error(None, str(error))
            else:
                # Permite que la página de confirmación vacíe el carrito del navegador una sola vez
                request.session["pedido_nuevo"] = str(pedido.codigo)
                return redirect("pedido_confirmado", codigo=pedido.codigo)
    else:
        form = PedidoForm()

    productos = [
        {
            "id": producto.pk,
            "name": producto.nombre,
            "icon": (producto.marca or producto.nombre)[:18],
            "imagen": producto.imagen.url if producto.imagen else '',
            "price": float(producto.precio_vigente),
            "stock": producto.cantidad,
        }
        for producto in Producto.objects.all()
    ]
    contexto = {
        "form": form,
        "productos_json": productos,
        "envio_gratis_desde": int(ENVIO_GRATIS_DESDE),
        "costo_envio": int(COSTO_ENVIO),
    }
    return render(request, "inventario/checkout.html", contexto)


def pedido_confirmado(request, codigo):
    pedido = get_object_or_404(Pedido, codigo=codigo)
    limpiar_carrito = request.session.get("pedido_nuevo") == str(pedido.codigo)
    if limpiar_carrito:
        del request.session["pedido_nuevo"]
    contexto = {
        "pedido": pedido,
        "items": pedido.items.all(),
        "limpiar_carrito": limpiar_carrito,
        "instrucciones_transferencia": settings.TRANSFERENCIA_INSTRUCCIONES,
    }
    return render(request, "inventario/pedido_confirmado.html", contexto)
