from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ProductoForm
from .models import Producto


class AccesoTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(nombre="Teclado", cantidad=3, precio=100)

    def test_lista_es_publica(self):
        respuesta = self.client.get(reverse("lista_productos"))
        self.assertEqual(respuesta.status_code, 200)

    def test_anonimo_no_puede_crear_editar_ni_eliminar(self):
        urls = [
            reverse("crear_producto"),
            reverse("editar_producto", args=[self.producto.pk]),
            reverse("eliminar_producto", args=[self.producto.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                respuesta = self.client.post(url, {"nombre": "Hack"})
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn("login", respuesta["Location"])
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())
        self.assertEqual(Producto.objects.count(), 1)

    def test_staff_puede_eliminar(self):
        staff = get_user_model().objects.create_user("admin", password="x", is_staff=True)
        self.client.force_login(staff)
        self.client.post(reverse("eliminar_producto", args=[self.producto.pk]))
        self.assertFalse(Producto.objects.exists())


class FormularioTests(TestCase):
    datos_base = {"nombre": "GPU", "cantidad": 1, "precio": "1000"}

    def test_oferta_requiere_precio_de_oferta(self):
        form = ProductoForm({**self.datos_base, "en_oferta": True})
        self.assertFalse(form.is_valid())
        self.assertIn("precio_oferta", form.errors)

    def test_precio_de_oferta_debe_ser_menor(self):
        form = ProductoForm({**self.datos_base, "en_oferta": True, "precio_oferta": "1000"})
        self.assertFalse(form.is_valid())

    def test_oferta_valida(self):
        form = ProductoForm({**self.datos_base, "en_oferta": True, "precio_oferta": "800"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["precio_oferta"], Decimal("800"))
