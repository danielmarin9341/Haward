from django.contrib import admin

from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "marca", "cantidad", "precio", "en_oferta", "precio_oferta")
    search_fields = ("nombre", "categoria", "marca", "referencia")
    list_filter = ("categoria", "marca", "en_oferta")
