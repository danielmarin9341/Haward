from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "categoria", "marca", "referencia", "imagen", "cantidad",
            "precio", "descripcion",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Teclado mecánico"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "cantidad": forms.NumberInput(attrs={"min": "0"}),
        }
