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
    list_display = ('ver_detalles', 'nombre', 'nombre_local', 'telefono', 'correo_electronico', 'ubicacion', 'imagen_thumbnail')
    list_per_page = 10
    search_fields = ('nombre', 'nombre_local', 'telefono', 'correo_electronico')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
    fieldsets = (
        ('Información de Contacto', {
            'fields': ('nombre', 'correo_electronico', 'telefono')
        }),
        ('Detalles del Local', {
            'fields': ('nombre_local', 'ubicacion', 'imagen')
        }),
    )

    def ver_detalles(self, obj):
        nombre = obj.nombre or "Dato aún no ingresado"
        nombre_local = obj.nombre_local or "Dato aún no ingresado"
        telefono = obj.telefono or "Dato aún no ingresado"
        correo = obj.correo_electronico or "Dato aún no ingresado"
        ubicacion = obj.ubicacion.nombre if obj.ubicacion else "Dato aún no ingresado"
        
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen and hasattr(obj.imagen, 'url') else "No hay imagen"

        modal_html = f"""
        <div id="modal-proveedor-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Proveedor: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-proveedor-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Información de Contacto</h4>
                                <p><strong>Nombre:</strong> {nombre}</p>
                                <p><strong>Teléfono:</strong> {telefono}</p>
                                <p><strong>Correo Electrónico:</strong> {correo}</p>
                            </div>
                            <div class="details-section">
                                <h4>Detalles del Local</h4>
                                <p><strong>Nombre del Local:</strong> {nombre_local}</p>
                                <p><strong>Ubicación:</strong> {ubicacion}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-proveedor-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

    def imagen_thumbnail(self, obj):
        if obj.imagen:
            return mark_safe(f'<a href="{obj.imagen.url}" target="_blank"><img src="{obj.imagen.url}" width="100" /></a>')
        return "Sin imagen"
    imagen_thumbnail.short_description = 'Vista Previa'


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('ver_detalles', 'nombre', 'barrio', 'direccion', 'link_con_icono', 'imagen_thumbnail')
    list_per_page = 10
    search_fields = ('nombre', 'barrio', 'direccion')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'imagen')
        }),
        ('Detalles de la Ubicación', {
            'fields': ('barrio', 'direccion', 'link')
        }),
    )

    def ver_detalles(self, obj):
        nombre = obj.nombre or "Dato aún no ingresado"
        barrio = obj.barrio or "Dato aún no ingresado"
        direccion = obj.direccion or "Dato aún no ingresado"
        link = f'<a href="{obj.link}" target="_blank">Abrir enlace</a>' if obj.link else "No disponible"
        
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen and hasattr(obj.imagen, 'url') else "No hay imagen"

        modal_html = f"""
        <div id="modal-ubicacion-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Ubicación: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-ubicacion-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Información de la Ubicación</h4>
                                <p><strong>Nombre:</strong> {nombre}</p>
                                <p><strong>Barrio:</strong> {barrio}</p>
                                <p><strong>Dirección:</strong> {direccion}</p>
                                <p><strong>Enlace:</strong> {link}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-ubicacion-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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