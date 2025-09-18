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
    list_display = ('identificador', 'raza', 'genero', 'edad', 'potrero', 'estado', 'vacunado', 'proxima_vacunacion', 'parto', 'imagen_thumbnail')
    list_filter = ('raza', 'genero', 'estado', 'potrero', 'vacunado')
    search_fields = ('identificador', 'raza')
    
    readonly_fields = ('edad', 'parto')

    fieldsets = (
        ('Información Principal', {
            'fields': ('identificador', 'raza', 'genero', 'potrero', 'imagen')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_nacimiento', 'edad', 'fecha_ingreso', 'estado')
        }),
        ('Salud y Reproducción', {
            'fields': ('vacunado', 'nombre_vacuna', 'proxima_vacunacion', 'parto')
        }),
    )

    def edad(self, obj):
        return obj.edad
    edad.short_description = 'Edad'

@admin.register(Medicamento)
class MedicamentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'lote', 'cantidad', 'fecha_caducidad', 'imagen_thumbnail')
    list_filter = ('fecha_caducidad',)
    search_fields = ('nombre', 'lote')

@admin.register(Alimento)
class AlimentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'ubicacion', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_filter = ('ubicacion', 'fecha_compra', 'fecha_vencimiento')
    search_fields = ('nombre', 'ubicacion__nombre')
    
    readonly_fields = ('cantidad_kg_usada', 'cantidad_kg_restante')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'ubicacion', 'imagen')
        }),
        ('Cantidad (en Kg)', {
            'fields': ('cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
    )

    def cantidad_kg_restante(self, obj):
        return obj.cantidad_kg_restante
    cantidad_kg_restante.short_description = 'Cantidad (Kg) Restante'

@admin.register(ControlPlaga)
class ControlPlagaAdmin(ImagenAdminMixin):
    list_display = ('nombre_producto', 'tipo', 'cantidad_ingresada_con_unidad', 'cantidad_usada_con_unidad', 'cantidad_restante_con_unidad', 'ubicacion', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_filter = ('tipo', 'ubicacion', 'fecha_compra', 'fecha_vencimiento')
    search_fields = ('nombre_producto', 'tipo', 'ubicacion__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')

    fieldsets = (
        (None, {
            'fields': ('nombre_producto', 'tipo', 'ubicacion', 'imagen')
        }),
        ('Cantidad', {
            'fields': (('cantidad_ingresada', 'unidad_medida'), 'cantidad_usada', 'cantidad_restante')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
    )

    def cantidad_ingresada_con_unidad(self, obj):
        return f"{obj.cantidad_ingresada} {obj.get_unidad_medida_display()}"
    cantidad_ingresada_con_unidad.short_description = 'Ingresado'

    def cantidad_usada_con_unidad(self, obj):
        return f"{obj.cantidad_usada} {obj.get_unidad_medida_display()}"
    cantidad_usada_con_unidad.short_description = 'Usado'
    
    def cantidad_restante_con_unidad(self, obj):
        return f"{obj.cantidad_restante} {obj.get_unidad_medida_display()}"
    cantidad_restante_con_unidad.short_description = 'Restante'

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
    list_display = ('tipo', 'cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'imagen_thumbnail')
    list_filter = ('tipo',)
    search_fields = ('tipo',)

    readonly_fields = ('cantidad_galones_usados', 'cantidad_galones_restantes')

    fieldsets = (
        (None, {
            'fields': ('tipo', 'imagen')
        }),
        ('Cantidad (en Galones)', {
            'fields': ('cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes')
        }),
    )

    def cantidad_galones_restantes(self, obj):
        return obj.cantidad_galones_restantes
    cantidad_galones_restantes.short_description = 'Galones Restantes'

# ... (resto del código de admin.py) ...
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        if obj:
            fieldsets = list(fieldsets)
            
            fieldsets[2] = (
                _('Permissions'),
                {'fields': ('is_active', 'is_staff', 'is_superuser')}
            )
            
            fieldsets[3] = (
                _('Important dates'),
                {'fields': ('last_login', 'date_joined')}
            )
        
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['date_joined'].label = 'Fecha de registro'
        return form

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)