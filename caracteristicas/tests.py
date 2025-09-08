from django.test import TestCase
from .models import Categoria, Proveedor, Ubicacion, Etiqueta

class CategoriaModelTest(TestCase):

    def test_str_representation(self):
        categoria = Categoria.objects.create(nombre="Lácteos")
        self.assertEqual(str(categoria), "Lácteos")

class ProveedorModelTest(TestCase):

    def test_str_representation(self):
        proveedor = Proveedor.objects.create(nombre="Proveedor A")
        self.assertEqual(str(proveedor), "Proveedor A")

class UbicacionModelTest(TestCase):

    def test_str_representation(self):
        ubicacion = Ubicacion.objects.create(nombre="Bodega 1")
        self.assertEqual(str(ubicacion), "Bodega 1")

from django.db.utils import IntegrityError

class EtiquetaModelTest(TestCase):

    def test_str_representation(self):
        etiqueta = Etiqueta.objects.create(nombre="Frágil")
        self.assertEqual(str(etiqueta), "Frágil")

    def test_nombre_is_unique(self):
        Etiqueta.objects.create(nombre="Urgente")
        with self.assertRaises(IntegrityError):
            Etiqueta.objects.create(nombre="Urgente")
