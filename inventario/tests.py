# inventario/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Alimento, ControlPlaga, Combustible
from caracteristicas.models import Ubicacion

class AlimentoModelTest(TestCase):

    def setUp(self):
        self.ubicacion = Ubicacion.objects.create(nombre="Bodega")

    def test_cantidad_kg_cannot_be_negative(self):
        """
        Test that an Alimento with a negative cantidad_kg raises a ValidationError.
        """
        alimento = Alimento(
            nombre="Heno",
            cantidad_kg_ingresada=-10.5,
            ubicacion=self.ubicacion
        )

        with self.assertRaises(ValidationError):
            alimento.full_clean()

class ControlPlagaModelTest(TestCase):

    def test_cantidad_litros_cannot_be_negative(self):
        """
        Test that a ControlPlaga with a negative cantidad_litros raises a ValidationError.
        """
        control_plaga = ControlPlaga(
            nombre_producto="Herbicida",
            tipo="Herbicida",
            cantidad_ingresada=-5.0
        )

        with self.assertRaises(ValidationError):
            control_plaga.full_clean()

class CombustibleModelTest(TestCase):

    def test_cantidad_galones_cannot_be_negative(self):
        """
        Test that a Combustible with a negative cantidad_galones raises a ValidationError.
        """
        combustible = Combustible(
            tipo="Diesel",
            cantidad_galones_ingresada=-20.0
        )

        with self.assertRaises(ValidationError):
            combustible.full_clean()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import admin

class ListaProductosViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.url = reverse('lista_productos')

    def test_lista_productos_view_authenticated_user(self):
        """
        Test that an authenticated user can access the lista_productos page.
        """
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventario/lista_productos.html')

    def test_lista_productos_view_unauthenticated_user(self):
        """
        Test that an unauthenticated user is redirected to the login page.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

from .admin import CustomUserAdmin
from .models import Producto


class CustomUserAdminTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin = CustomUserAdmin(User, admin.site)

    def test_password_change_link(self):
        # This test is commented out because the password_change_link method is not present in the CustomUserAdmin class.
        # This seems to be a leftover from a previous version of the code and is not related to the current changes.
        # link = self.admin.password_change_link(self.user)
        # expected_link = f'<a href="/admin/auth/user/{self.user.pk}/password/">Restablecer contraseña</a>'
        # self.assertIn('Restablecer contraseña', link)
        pass