# caracteristicas/models.py
from django.db import models
from cloudinary.models import CloudinaryField

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField("Nombre del proveedor", max_length=100)
    nombre_local = models.CharField("Nombre del lugar/local", max_length=100, blank=True)
    correo_electronico = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True, help_text="Número de teléfono del proveedor")
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.SET_NULL, null=True, blank=True)
    imagen = CloudinaryField('image', folder='proveedores', null=True, blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        # Construimos un texto descriptivo para que aparezca en los menús desplegables
        info = f"{self.nombre}"
        if self.nombre_local:
            info += f" ({self.nombre_local})"
        if self.telefono:
            info += f" - {self.telefono}"
        return info

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    barrio = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True, help_text="Enlace a la ubicación en un mapa")
    imagen = CloudinaryField('image', folder='ubicaciones', null=True, blank=True)

    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

    def __str__(self):
        # --- ESTA ES LA LÍNEA CLAVE ---
        # Formateamos el texto para que sea más descriptivo
        detalles = []
        if self.barrio:
            detalles.append(self.barrio)
        if self.direccion:
            detalles.append(self.direccion)
        
        if detalles:
            return f"{self.nombre} ({' - '.join(detalles)})"
        return self.nombre

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Frágil, Urgente, Vacunado")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_etiquetas')
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'

    def __str__(self):
        return self.nombre