from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm
from .models import Producto


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
            "spec": producto.descripcion or producto.referencia or producto.marca or "Hardware",
            "price": producto.precio,
            "stock": producto.cantidad,
            "icon": (producto.marca or producto.nombre)[:18],
            "image": producto.imagen_url,
        }
        for producto in productos
    ]
    contexto = {
        "productos_json": datos_tienda,
        "total_productos": Producto.objects.count(),
        "total_unidades": Producto.objects.aggregate(total=Sum("cantidad"))["total"] or 0,
    }
    return render(request, "inventario/lista.html", contexto)


def crear_producto(request):
    form = ProductoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto agregado al inventario.")
        return redirect("lista_productos")
    return render(request, "inventario/formulario.html", {"form": form, "titulo": "Agregar producto"})


def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Producto actualizado.")
        return redirect("lista_productos")
    return render(request, "inventario/formulario.html", {"form": form, "titulo": "Editar producto"})


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado del inventario.")
        return redirect("lista_productos")
    return render(request, "inventario/confirmar_eliminacion.html", {"producto": producto})
