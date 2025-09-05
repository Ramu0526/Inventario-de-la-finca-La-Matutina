from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores' # <-- Corregido

    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones' # <-- Corregido

    def __str__(self):
        return self.nombre

# --- NUEVO MODELO AÑADIDO ---
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Frágil, Urgente, Vacunado")
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'

    def __str__(self):
        return self.nombre