# caracteristicas/admin.py
from django.contrib import admin
from .models import Categoria, Proveedor, Ubicacion, Etiqueta
from django.utils.html import mark_safe

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    search_fields = ('nombre', 'telefono')

@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'link_con_icono', 'imagen_thumbnail')
    search_fields = ('nombre',)

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


# --- GESTIÓN DE ETIQUETAS Y SUB-ETIQUETAS (VERSIÓN CORREGIDA) ---

class SubEtiquetaInline(admin.TabularInline):
    model = Etiqueta
    extra = 1
    fk_name = 'parent'
    verbose_name = "Sub-etiqueta"
    verbose_name_plural = "Sub-etiquetas"
    
    # Ocultamos el campo 'parent' en el formulario de la sub-etiqueta
    # para que sea más limpio, ya que se asigna automáticamente.
    fields = ('nombre',)


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    # Cambiamos 'parent' por la nueva función que lista las sub-etiquetas
    list_display = ('nombre', 'mostrar_sub_etiquetas')
    search_fields = ('nombre',)
    inlines = [SubEtiquetaInline]

    def mostrar_sub_etiquetas(self, obj):
        """
        Crea una lista con los nombres de las sub-etiquetas para mostrarla
        en el panel de administración.
        """
        # Buscamos todas las etiquetas que tienen a 'obj' como padre
        sub_etiquetas = obj.sub_etiquetas.all()
        if sub_etiquetas:
            return ", ".join([sub.nombre for sub in sub_etiquetas])
        return "Ninguna"
    mostrar_sub_etiquetas.short_description = 'Sub-etiquetas contenidas'

    def get_queryset(self, request):
        """
        Nos aseguramos de que la lista principal solo muestre
        las etiquetas que NO tienen padre.
        """
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)

    def get_fieldsets(self, request, obj=None):
        """
        Este es el cambio clave: Ocultamos el campo 'parent'
        del formulario principal de 'Etiqueta'.
        """
        # Definimos que el formulario solo debe mostrar el campo 'nombre'
        fieldsets = (
            (None, {
                'fields': ('nombre',),
            }),
        )
        return fieldsets