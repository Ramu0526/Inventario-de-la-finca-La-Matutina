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
    list_display = ('nombre', 'cantidad_con_unidad', 'categoria', 'precio', 'proveedor', 'fecha_produccion', 'fecha_venta', 'imagen_thumbnail')
    list_filter = ('categoria', 'proveedor', 'ubicacion', 'unidad_medida')
    search_fields = ('nombre', 'categoria__nombre', 'proveedor__nombre')

    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'proveedor', 'ubicacion', 'imagen')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad', 'unidad_medida'), 'precio')
        }),
        ('Fechas', {
            'fields': ('fecha_produccion', 'fecha_venta')
        }),
    )

    def cantidad_con_unidad(self, obj):
        return f"{obj.cantidad} {obj.get_unidad_medida_display()}"
    cantidad_con_unidad.short_description = 'Cantidad'

@admin.register(Ganado)
class GanadoAdmin(ImagenAdminMixin):
    list_display = ('identificador', 'raza', 'genero', 'edad', 'potrero', 'fecha_nacimiento', 'fecha_ingreso', 'estado', 'nombre_vacuna', 'proxima_vacunacion', 'imagen_thumbnail')
    list_filter = ('raza', 'genero', 'estado', 'potrero', 'vacunado')
    search_fields = ('identificador', 'raza', 'nombre_vacuna')
    
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
    list_display = ('nombre', 'cantidad_restante_con_unidad', 'categoria', 'precio', 'ubicacion', 'f_compra', 'f_ingreso', 'f_vencimiento', 'imagen_thumbnail')
    list_filter = ('categoria', 'ubicacion', 'fecha_compra', 'fecha_ingreso', 'fecha_vencimiento')
    search_fields = ('nombre',)
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'ubicacion', 'imagen')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad_ingresada', 'unidad_medida'), 'cantidad_usada', 'cantidad_restante', 'precio')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_ingreso', 'fecha_vencimiento')
        }),
    )

    def cantidad_restante_con_unidad(self, obj):
        return f"{obj.cantidad_restante} {obj.get_unidad_medida_display()}"
    cantidad_restante_con_unidad.short_description = 'Restante'
    
    # --- FUNCIONES PARA ACORTAR ENCABEZADOS ---
    def f_compra(self, obj):
        return obj.fecha_compra
    f_compra.short_description = 'F. Compra'

    def f_ingreso(self, obj):
        return obj.fecha_ingreso
    f_ingreso.short_description = 'F. Ingreso'

    def f_vencimiento(self, obj):
        return obj.fecha_vencimiento
    f_vencimiento.short_description = 'F. Vencimiento'


@admin.register(Alimento)
class AlimentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'precio', 'proveedor', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_filter = ('ubicacion', 'proveedor', 'fecha_vencimiento')
    search_fields = ('nombre', 'ubicacion__nombre', 'proveedor__nombre')
    
    readonly_fields = ('cantidad_kg_usada', 'cantidad_kg_restante')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'proveedor', 'ubicacion', 'imagen')
        }),
        ('Cantidad y Precio (en Kg)', {
            'fields': ('cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'precio')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
    )

    def cantidad_kg_restante(self, obj):
        return f"{obj.cantidad_kg_ingresada - obj.cantidad_kg_usada} Kg"
    cantidad_kg_restante.short_description = 'Cantidad Restante'

@admin.register(ControlPlaga)
class ControlPlagaAdmin(ImagenAdminMixin):
    list_display = ('nombre_producto', 'tipo', 'cantidad_ingresada_con_unidad', 'cantidad_usada_con_unidad', 'cantidad_restante_con_unidad', 'precio', 'proveedor', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_filter = ('tipo', 'proveedor', 'ubicacion', 'fecha_vencimiento')
    search_fields = ('nombre_producto', 'tipo', 'ubicacion__nombre', 'proveedor__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')

    fieldsets = (
        (None, {
            'fields': ('nombre_producto', 'tipo', 'proveedor', 'ubicacion', 'imagen')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad_ingresada', 'unidad_medida'), 'cantidad_usada', 'cantidad_restante', 'precio')
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
    list_display = ('nombre', 'tamano', 'area_hectareas', 'imagen_thumbnail')
    list_filter = ('tamano',)
    search_fields = ('nombre',)
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'imagen')
        }),
        ('Detalles del Potrero', {
            'fields': ('tamano', 'area_hectareas')
        }),
    )

@admin.register(Mantenimiento)
class MantenimientoAdmin(ImagenAdminMixin):
    list_display = ('equipo', 'fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento', 'completado', 'imagen_thumbnail')
    list_filter = ('completado', 'fecha_proximo_mantenimiento')
    search_fields = ('equipo',)
    
    fieldsets = (
        (None, {
            'fields': ('equipo', 'imagen')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento', 'completado')
        }),
    )

@admin.register(Combustible)
class CombustibleAdmin(ImagenAdminMixin):
    list_display = ('tipo', 'cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio', 'imagen_thumbnail')
    list_filter = ('tipo',)
    search_fields = ('tipo',)

    readonly_fields = ('cantidad_galones_usados', 'cantidad_galones_restantes')

    fieldsets = (
        (None, {
            'fields': ('tipo', 'imagen')
        }),
        ('Cantidad y Precio (en Galones)', {
            'fields': ('cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio')
        }),
    )

    def cantidad_galones_restantes(self, obj):
        return f"{obj.cantidad_galones_ingresada - obj.cantidad_galones_usados} gal"
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
        # --- ESTA ES LA CORRECCIÓN ---
        # Solo intentamos cambiar la etiqueta si el campo existe en el formulario
        if 'date_joined' in form.base_fields:
            form.base_fields['date_joined'].label = 'Fecha de registro'
        return form

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)