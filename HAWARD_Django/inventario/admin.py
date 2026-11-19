from django.contrib import admin
from django.db import transaction
from django.db.models import F

from .models import Pedido, PedidoItem, Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "marca", "cantidad", "precio", "en_oferta", "precio_oferta")
    search_fields = ("nombre", "categoria", "marca", "referencia")
    list_filter = ("categoria", "marca", "en_oferta")


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    can_delete = False
    fields = ("nombre", "precio_unitario", "cantidad")
    readonly_fields = ("nombre", "precio_unitario", "cantidad")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("referencia", "nombre", "ciudad", "metodo_pago", "total", "estado", "creado")
    list_filter = ("estado", "metodo_pago", "creado")
    search_fields = ("nombre", "email", "telefono", "ciudad")
    date_hierarchy = "creado"
    inlines = [PedidoItemInline]
    # El estado solo cambia con las acciones de abajo, para que cancelar siempre devuelva el stock
    readonly_fields = (
        "codigo", "estado", "nombre", "email", "telefono", "direccion", "ciudad", "notas",
        "metodo_pago", "subtotal", "envio", "total", "creado",
    )
    actions = ["marcar_pagado", "marcar_enviado", "marcar_entregado", "cancelar_y_devolver_stock"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="Referencia")
    def referencia(self, obj):
        return obj.referencia

    def _cambiar_estado(self, request, queryset, desde, nuevo, etiqueta):
        cantidad = queryset.filter(estado__in=desde).update(estado=nuevo)
        self.message_user(request, f"{cantidad} pedido(s) marcados como {etiqueta}.")

    @admin.action(description="Marcar como pagado")
    def marcar_pagado(self, request, queryset):
        self._cambiar_estado(request, queryset, [Pedido.Estado.PENDIENTE], Pedido.Estado.PAGADO, "pagados")

    @admin.action(description="Marcar como enviado")
    def marcar_enviado(self, request, queryset):
        # Contra entrega puede enviarse sin estar pagado todavía
        self._cambiar_estado(
            request, queryset, [Pedido.Estado.PENDIENTE, Pedido.Estado.PAGADO],
            Pedido.Estado.ENVIADO, "enviados",
        )

    @admin.action(description="Marcar como entregado")
    def marcar_entregado(self, request, queryset):
        self._cambiar_estado(request, queryset, [Pedido.Estado.ENVIADO], Pedido.Estado.ENTREGADO, "entregados")

    @admin.action(description="Cancelar pedidos y devolver el stock")
    def cancelar_y_devolver_stock(self, request, queryset):
        cancelados = 0
        with transaction.atomic():
            pedidos = queryset.exclude(
                estado__in=[Pedido.Estado.CANCELADO, Pedido.Estado.ENTREGADO]
            ).prefetch_related("items")
            for pedido in pedidos:
                for item in pedido.items.all():
                    if item.producto_id:
                        Producto.objects.filter(pk=item.producto_id).update(
                            cantidad=F("cantidad") + item.cantidad
                        )
                pedido.estado = Pedido.Estado.CANCELADO
                pedido.save(update_fields=["estado"])
                cancelados += 1
        self.message_user(request, f"{cancelados} pedido(s) cancelados y con el stock devuelto.")
