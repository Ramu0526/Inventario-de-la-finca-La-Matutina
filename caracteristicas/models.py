from django.db import models

# Mantenemos los modelos que se moverán a 'caracteristicas' por ahora
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self): return self.nombre