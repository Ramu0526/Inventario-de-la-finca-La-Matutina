from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    Producto, Ganado, Medicamento, Alimento, ControlPlaga, 
    Potrero, Mantenimiento, Combustible
)

# --- 1. Clase Base para Modelos con Imagen ---

class ImagenAdminMixin(admin.ModelAdmin):
    """
    Mixin para añadir una vista previa de la imagen en el listado del admin.
    """
    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return mark_safe(f'<img src="{obj.imagen.url}" width="100" />')
        return "Sin imagen"
    imagen_thumbnail.short_description = 'Vista Previa'

# --- 2. Clases de Personalización del Admin ---

@admin.register(Producto)
class ProductoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'cantidad', 'categoria', 'imagen_thumbnail')
    list_filter = ('categoria', 'proveedor', 'ubicacion')
    search_fields = ('nombre', 'categoria__nombre', 'proveedor__nombre')

@admin.register(Ganado)
class GanadoAdmin(ImagenAdminMixin):
    list_display = ('identificador', 'raza', 'potrero', 'imagen_thumbnail')
    list_filter = ('raza', 'potrero')
    search_fields = ('identificador', 'raza')

@admin.register(Medicamento)
class MedicamentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'lote', 'cantidad', 'fecha_caducidad', 'imagen_thumbnail')
    list_filter = ('fecha_caducidad',)
    search_fields = ('nombre', 'lote')

@admin.register(Alimento)
class AlimentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'cantidad_kg', 'ubicacion', 'imagen_thumbnail')
    list_filter = ('ubicacion',)
    search_fields = ('nombre',)

@admin.register(ControlPlaga)
class ControlPlagaAdmin(ImagenAdminMixin):
    list_display = ('nombre_producto', 'tipo', 'cantidad_litros', 'imagen_thumbnail')
    list_filter = ('tipo',)
    search_fields = ('nombre_producto',)

@admin.register(Potrero)
class PotreroAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'area_hectareas', 'imagen_thumbnail')
    search_fields = ('nombre',)

@admin.register(Mantenimiento)
class MantenimientoAdmin(ImagenAdminMixin):
    list_display = ('equipo', 'fecha_programada', 'completado', 'imagen_thumbnail')
    list_filter = ('completado', 'fecha_programada')
    search_fields = ('equipo', 'descripcion_tarea')

@admin.register(Combustible)
class CombustibleAdmin(ImagenAdminMixin):
    list_display = ('tipo', 'cantidad_galones', 'imagen_thumbnail')
    list_filter = ('tipo',)
    search_fields = ('tipo',)

# Nota: La personalización del modelo User se ha eliminado de este archivo
# para mantenerlo enfocado únicamente en la app 'inventario'. 
# Si se necesita, debería estar en el admin.py de una app de 'core' o 'users'.