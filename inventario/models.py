# inventario/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField

# --- NUEVOS MODELOS PARA 'INVENTARIO' ---

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    # Conectamos con los modelos que estarán en la otra app
    categoria = models.ForeignKey('caracteristicas.Categoria', on_delete=models.SET_NULL, null=True)
    proveedor = models.ForeignKey('caracteristicas.Proveedor', on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True, blank=True)
    imagen = CloudinaryField('image', folder='productos', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Ganado(models.Model):
    identificador = models.CharField(max_length=50, unique=True, help_text="Ej: Arete N° 123")
    raza = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    potrero = models.ForeignKey('Potrero', on_delete=models.SET_NULL, null=True, blank=True)
    imagen = CloudinaryField('image', folder='ganado', null=True, blank=True)
    def __str__(self): return self.identificador

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    lote = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField(help_text="Unidades, ml, etc.")
    fecha_caducidad = models.DateField()
    imagen = CloudinaryField('image', folder='medicamentos', null=True, blank=True)
    def __str__(self): return f"{self.nombre} (Lote: {self.lote})"

class Alimento(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Heno, Silo de maíz, Sal mineral")
    cantidad_kg = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    ubicacion = models.ForeignKey('caracteristicas.Ubicacion', on_delete=models.SET_NULL, null=True)
    imagen = CloudinaryField('image', folder='alimentos', null=True, blank=True)
    def __str__(self): return self.nombre

class ControlPlaga(models.Model):
    nombre_producto = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, help_text="Ej: Herbicida, Insecticida")
    cantidad_litros = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    imagen = CloudinaryField('image', folder='control_plagas', null=True, blank=True)
    def __str__(self): return self.nombre_producto

class Potrero(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Potrero La Loma")
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = CloudinaryField('image', folder='potreros', null=True, blank=True)
    def __str__(self): return self.nombre

class Mantenimiento(models.Model):
    equipo = models.CharField(max_length=100, help_text="Ej: Tractor, Guadaña")
    descripcion_tarea = models.TextField()
    fecha_programada = models.DateField()
    completado = models.BooleanField(default=False)
    imagen = CloudinaryField('image', folder='mantenimiento', null=True, blank=True)
    def __str__(self): return f"Mantenimiento de {self.equipo} - {self.fecha_programada}"

class Combustible(models.Model):
    tipo = models.CharField(max_length=50, help_text="Ej: Diesel, Gasolina")
    cantidad_galones = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    imagen = CloudinaryField('image', folder='combustible', null=True, blank=True)
    def __str__(self): return f"{self.cantidad_galones} galones de {self.tipo}"