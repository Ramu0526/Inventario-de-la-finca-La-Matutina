from django.contrib import admin
from .models import Categoria, Proveedor, Ubicacion, Etiqueta
from django.utils.html import mark_safe

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    list_per_page = 10

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nombre_local', 'telefono', 'correo_electronico', 'ubicacion', 'imagen_thumbnail')
    list_per_page = 10
    search_fields = ('nombre', 'nombre_local', 'telefono', 'correo_electronico')
    
    fieldsets = (
        ('Información de Contacto', {
            'fields': ('nombre', 'correo_electronico', 'telefono')
        }),
        ('Detalles del Local', {
            'fields': ('nombre_local', 'ubicacion', 'imagen')
        }),
    )

    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return mark_safe(f'<a href="{obj.imagen.url}" target="_blank"><img src="{obj.imagen.url}" width="100" /></a>')
        return "Sin imagen"
    imagen_thumbnail.short_description = 'Vista Previa'


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'barrio', 'direccion', 'link_con_icono', 'imagen_thumbnail')
    list_per_page = 10
    search_fields = ('nombre', 'barrio', 'direccion')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'imagen')
        }),
        ('Detalles de la Ubicación', {
            'fields': ('barrio', 'direccion', 'link')
        }),
    )

    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return mark_safe(f'<a href="{obj.imagen.url}" target="_blank"><img src="{obj.imagen.url}" width="100" /></a>')
        return "Sin imagen"
    imagen_thumbnail.short_description = 'Vista Previa'

    def link_con_icono(self, obj):
        if obj.link:
            return mark_safe(f'<a href="{obj.link}" target="_blank">Ver ubicación 📍</a>')
        return "Sin enlace"
    link_con_icono.short_description = 'Enlace de Ubicación'

class SubEtiquetaInline(admin.TabularInline):
    model = Etiqueta
    extra = 1
    fk_name = 'parent'
    verbose_name = "Sub-etiqueta"
    verbose_name_plural = "Sub-etiquetas"
    fields = ('nombre',)


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mostrar_sub_etiquetas')
    list_per_page = 10
    search_fields = ('nombre',)
    inlines = [SubEtiquetaInline]

    def mostrar_sub_etiquetas(self, obj):
        sub_etiquetas = obj.sub_etiquetas.all()
        if sub_etiquetas:
            return ", ".join([sub.nombre for sub in sub_etiquetas])
        return "Ninguna"
    mostrar_sub_etiquetas.short_description = 'Sub-etiquetas contenidas'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': ('nombre',),
            }),
        )
        return fieldsets