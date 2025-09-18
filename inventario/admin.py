from django.contrib import admin
from django.utils.html import mark_safe
from .models import (
    Producto, Ganado, Medicamento, Alimento, ControlPlaga,
    Potrero, Mantenimiento, Combustible
)

# --- 1. Clase Base para Modelos con Imagen ---

class ImagenAdminMixin(admin.ModelAdmin):
    """
    Mixin para añadir una vista previa de la imagen que se puede ampliar.
    """
    def imagen_thumbnail(self, obj):
        if obj.imagen:
            # Envolvemos la imagen en un enlace <a> para hacerla clicable
            return mark_safe(f'<a href="{obj.imagen.url}" target="_blank"><img src="{obj.imagen.url}" width="100" /></a>')
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

# inventario/admin.py

# ... (todo tu código anterior de ProductoAdmin, GanadoAdmin, etc. va aquí) ...


# --- 3. PERSONALIZACIÓN DEL ADMIN DE USUARIOS (VERSIÓN DEFINITIVA) ---
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

# --- Paso A: Ocultar el modelo de "Grupos" ---
admin.site.unregister(Group)

# --- Paso B: Crear una vista de Admin personalizada para el Usuario ---
class CustomUserAdmin(UserAdmin):
    
    def get_fieldsets(self, request, obj=None):
        """
        Modifica dinámicamente los fieldsets para eliminar los permisos
        y cambiar el título de la sección de fechas.
        """
        # Llama al método original para obtener los fieldsets por defecto
        fieldsets = super().get_fieldsets(request, obj)
        
        # Si estamos en el formulario de edición (no de creación)
        if obj:
            # Convertimos a lista para poder modificarlo
            fieldsets = list(fieldsets)
            
            # Buscamos y modificamos la sección de "Permisos"
            # para quitar los campos 'groups' y 'user_permissions'
            fieldsets[2] = (
                _('Permissions'),
                {'fields': ('is_active', 'is_staff', 'is_superuser')}
            )
            
            # Cambiamos el título de la sección de fechas
            fieldsets[3] = (
                _('Fechas Importantes'),
                {'fields': ('last_login', 'date_joined')}
            )
        
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Modifica el formulario para cambiar la etiqueta de 'date_joined'.
        """
        form = super().get_form(request, obj, **kwargs)
        # Cambiamos la etiqueta aquí
        form.base_fields['date_joined'].label = 'Fecha de registro'
        return form

# --- Paso C: Registrar nuestra configuración personalizada ---
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)