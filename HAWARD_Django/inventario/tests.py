import json
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .forms import ProductoForm
from .models import Pedido, Producto
from .pedidos import CarritoError, parsear_carrito

# En las pruebas no existe el manifiesto de collectstatic, así que se usa el almacenamiento simple
ESTATICOS_SIMPLES = override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})


@ESTATICOS_SIMPLES
class AccesoTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(nombre="Teclado", cantidad=3, precio=100)
        # Las migraciones ya cargan el catálogo, así que se compara contra el total de partida
        self.total_inicial = Producto.objects.count()

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
        self.assertEqual(Producto.objects.count(), self.total_inicial)

    def test_staff_puede_eliminar(self):
        staff = get_user_model().objects.create_user("admin", password="x", is_staff=True)
        self.client.force_login(staff)
        self.client.post(reverse("eliminar_producto", args=[self.producto.pk]))
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())


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


class ParsearCarritoTests(SimpleTestCase):
    def test_carrito_valido(self):
        self.assertEqual(parsear_carrito('{"1": 2, "7": 1}'), {1: 2, 7: 1})

    def test_rechaza_entradas_invalidas(self):
        invalidos = ["", "no es json", "[]", "{}", '{"a": 1}', '{"1": 0}', '{"1": -3}',
                     '{"1": 1.5}', '{"1": true}', '{"1": "2"}', '{"1": 100}']
        for texto in invalidos:
            with self.subTest(texto=texto):
                with self.assertRaises(CarritoError):
                    parsear_carrito(texto)


@ESTATICOS_SIMPLES
class PagoTests(TestCase):
    def setUp(self):
        self.a = Producto.objects.create(nombre="Mouse", cantidad=5, precio=100000)
        self.b = Producto.objects.create(
            nombre="Teclado", cantidad=2, precio=200000, en_oferta=True, precio_oferta=150000,
        )

    def datos(self, carrito, **extra):
        datos = {
            "nombre": "Ana Pérez", "email": "ana@example.com", "telefono": "3001234567",
            "direccion": "Calle 1 # 2-3", "ciudad": "Bogotá", "notas": "",
            "metodo_pago": "contra_entrega", "carrito": json.dumps(carrito),
        }
        datos.update(extra)
        return datos

    def test_pagina_de_pago_es_publica(self):
        self.assertEqual(self.client.get(reverse("checkout")).status_code, 200)

    def test_crea_pedido_con_precios_del_servidor_y_descuenta_stock(self):
        respuesta = self.client.post(
            reverse("checkout"), self.datos({str(self.a.pk): 2, str(self.b.pk): 1})
        )
        pedido = Pedido.objects.get()
        self.assertRedirects(respuesta, reverse("pedido_confirmado", args=[pedido.codigo]))
        self.assertEqual(pedido.subtotal, Decimal("350000"))  # 2 × 100.000 + 1 × 150.000 (oferta)
        self.assertEqual(pedido.envio, Decimal("15000"))
        self.assertEqual(pedido.total, Decimal("365000"))
        self.assertEqual(pedido.estado, Pedido.Estado.PENDIENTE)
        self.assertEqual(pedido.items.count(), 2)
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual((self.a.cantidad, self.b.cantidad), (3, 1))

    def test_envio_gratis_desde_500000(self):
        self.client.post(reverse("checkout"), self.datos({str(self.a.pk): 5}))
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.envio, Decimal("0"))
        self.assertEqual(pedido.total, Decimal("500000"))

    def test_no_vende_mas_que_el_stock(self):
        respuesta = self.client.post(reverse("checkout"), self.datos({str(self.a.pk): 6}))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Solo quedan 5")
        self.assertFalse(Pedido.objects.exists())
        self.a.refresh_from_db()
        self.assertEqual(self.a.cantidad, 5)

    def test_rechaza_carrito_vacio_o_producto_inexistente(self):
        for carrito in ({}, {"99999": 1}):
            with self.subTest(carrito=carrito):
                respuesta = self.client.post(reverse("checkout"), self.datos(carrito))
                self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Pedido.objects.exists())

    def test_valida_datos_del_cliente(self):
        respuesta = self.client.post(
            reverse("checkout"), self.datos({str(self.a.pk): 1}, telefono="abc", email="no-es-correo"),
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Pedido.objects.exists())
        self.a.refresh_from_db()
        self.assertEqual(self.a.cantidad, 5)

    def test_confirmacion_muestra_pedido_y_limpia_carrito_una_vez(self):
        self.client.post(reverse("checkout"), self.datos({str(self.a.pk): 1}))
        pedido = Pedido.objects.get()
        url = reverse("pedido_confirmado", args=[pedido.codigo])
        primera = self.client.get(url)
        self.assertContains(primera, pedido.referencia)
        self.assertContains(primera, "localStorage.removeItem")
        self.assertNotContains(self.client.get(url), "localStorage.removeItem")

    def test_codigo_desconocido_da_404(self):
        self.assertEqual(self.client.get(reverse("pedido_confirmado", args=[uuid.uuid4()])).status_code, 404)

    def test_cancelar_desde_el_admin_devuelve_el_stock(self):
        self.client.post(reverse("checkout"), self.datos({str(self.a.pk): 2}))
        pedido = Pedido.objects.get()
        admin = get_user_model().objects.create_superuser("root", "root@example.com", "x")
        self.client.force_login(admin)
        self.client.post(
            reverse("admin:inventario_pedido_changelist"),
            {"action": "cancelar_y_devolver_stock", "_selected_action": [pedido.pk]},
        )
        pedido.refresh_from_db()
        self.a.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.CANCELADO)
        self.assertEqual(self.a.cantidad, 5)
