from django import forms

from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre", "categoria", "marca", "referencia", "imagen", "cantidad",
            "precio", "en_oferta", "precio_oferta", "descripcion",
        ]
        widgets = {
            "precio_oferta": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Teclado mecánico"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "cantidad": forms.NumberInput(attrs={"min": "0"}),
        }

    def clean(self):
        datos = super().clean()
        en_oferta = datos.get("en_oferta")
        precio = datos.get("precio")
        precio_oferta = datos.get("precio_oferta")
        if en_oferta and precio_oferta is None:
            self.add_error("precio_oferta", "Indica el precio de oferta si el producto está en promoción.")
        elif precio_oferta is not None and precio is not None and precio_oferta >= precio:
            self.add_error("precio_oferta", "El precio de oferta debe ser menor que el precio unitario.")
        return datos
