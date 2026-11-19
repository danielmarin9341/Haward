import re

from django import forms

from .models import Pedido, Producto


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


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["nombre", "email", "telefono", "direccion", "ciudad", "notas", "metodo_pago"]
        widgets = {
            "nombre": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Nombre y apellido"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "tucorreo@ejemplo.com"}),
            "telefono": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "placeholder": "3001234567"}),
            "direccion": forms.TextInput(attrs={"autocomplete": "street-address", "placeholder": "Calle 123 # 45-67, apto 801"}),
            "ciudad": forms.TextInput(attrs={"autocomplete": "address-level2", "placeholder": "Bogotá"}),
            "notas": forms.Textarea(attrs={"rows": 3, "placeholder": "Indicaciones para la entrega (opcional)"}),
            "metodo_pago": forms.RadioSelect(),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if not re.fullmatch(r"\+?[\d\s()-]{7,20}", telefono):
            raise forms.ValidationError("Ingresa un teléfono válido, por ejemplo 3001234567.")
        return telefono
