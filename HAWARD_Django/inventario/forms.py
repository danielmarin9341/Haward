from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "categoria", "marca", "referencia", "imagen_url", "cantidad",
            "precio", "descripcion",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Teclado mecánico"}),
            "imagen_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "cantidad": forms.NumberInput(attrs={"min": "0"}),
        }
