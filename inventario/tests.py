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
            cantidad_kg=-10.5,
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
            cantidad_litros=-5.0
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
            cantidad_galones=-20.0
        )

        with self.assertRaises(ValidationError):
            combustible.full_clean()
