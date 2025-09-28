from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from caracteristicas.models import Etiqueta
from .models import (
    Producto, Ganado, Medicamento, Alimento, ControlPlaga,
    Potrero, Mantenimiento, Combustible, Trabajador, Dotacion, Pago, LugarMantenimiento,
    Animal, Vacuna, RegistroVacunacion, Comprador, VentaProducto, RegistroMedicamento
)

class ImagenAdminMixin(admin.ModelAdmin):
    """
    Mixin para añadir una vista previa de la imagen que se puede ampliar.
    """
    def imagen_thumbnail(self, obj):
        if obj.imagen:
            try:
                return mark_safe(f'<a href="{obj.imagen.url}" target="_blank"><img src="{obj.imagen.url}" width="100" /></a>')
            except (AttributeError, ValueError):
                return "No se pudo cargar la imagen"
        return "Sin imagen"
    imagen_thumbnail.short_description = 'Vista Previa'

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    list_per_page = 10

@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono')
    search_fields = ('nombre',)
    list_per_page = 10

class VentaProductoInline(admin.TabularInline):
    model = VentaProducto
    extra = 1
    autocomplete_fields = ['comprador']

@admin.register(Producto)
class ProductoAdmin(ImagenAdminMixin):
    # CAMBIA la línea 'list_display' para incluir el estado
    list_display = ('nombre', 'cantidad_con_unidad', 'categoria', 'estado', 'precio', 'precio_total_display', 'fecha_produccion', 'fecha_venta', 'imagen_thumbnail')
    list_per_page = 10
    # AÑADE 'estado' a los filtros
    list_filter = ('categoria', 'estado', 'ubicaciones', 'unidad_medida')
    search_fields = ('nombre', 'categoria__nombre')

    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'ubicaciones', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad', 'unidad_medida'), 'precio')
        }),
        ('Fechas', {
            'fields': ('fecha_produccion', 'fecha_venta')
        }),
    )
    
    inlines = [VentaProductoInline]

    def cantidad_con_unidad(self, obj):
        return f"{obj.cantidad} {obj.get_unidad_medida_display()}"
    cantidad_con_unidad.short_description = 'Cantidad'
    
    def precio_total_display(self, obj):
        return f"${obj.precio_total:,.2f}"
    precio_total_display.short_description = 'Precio Total'

class RegistroVacunacionInline(admin.TabularInline):
    model = RegistroVacunacion
    fields = ('vacuna', 'fecha_aplicacion', 'fecha_proxima_dosis', 'notas')
    readonly_fields = ()
    can_delete = True
    extra = 1
    autocomplete_fields = ['vacuna']

class RegistroMedicamentoInline(admin.TabularInline):
    model = RegistroMedicamento
    fields = ('medicamento', 'fecha_aplicacion', 'notas')
    autocomplete_fields = ['medicamento']
    extra = 1

@admin.register(Ganado)
class GanadoAdmin(ImagenAdminMixin):
    list_display = ('identificador', 'animal', 'raza', 'genero', 'peso_kg', 'edad', 
                        'crecimiento', 'fecha_nacimiento', 'estado', 'estado_salud', 
                        #'razon_venta', 'razon_fallecimiento', # <--- COMENTA ESTOS
                        'peñe', 'historial_vacunacion', 'proximas_vacunas', 'imagen_thumbnail')
    # --- FIN DE LA MODIFICACIÓN ---
    list_per_page = 10
    list_filter = ('animal', 'genero', 'estado', 'estado_salud', 'crecimiento', 'peñe')
    search_fields = ('identificador', 'animal__nombre', 'raza')
    list_editable = ('estado_salud', 'crecimiento', 'estado')
    
    readonly_fields = ('edad',)

    fieldsets = (
        ('Información Principal', {
            'fields': ('identificador', 'animal', 'raza', 'genero', 'peso_kg', 'crecimiento', 'imagen', 'descripcion')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_nacimiento', 'edad', 'estado', 'estado_salud')
        }),
        ('Información de Peñe', {
            'fields': ('peñe', 'fecha_peñe', 'descripcion_peñe')
        }),
        ('Información de Venta', {
            'classes': ('collapse',),
            'fields': ('fecha_venta', 'valor_venta', 'razon_venta', 'comprador', 'comprador_telefono')
        }),
        ('Información de Fallecimiento', {
            'classes': ('collapse',),
            'fields': ('fecha_fallecimiento', 'razon_fallecimiento')
        }),
    )

    inlines = [RegistroVacunacionInline, RegistroMedicamentoInline]

    def edad(self, obj):
        # Añadimos un print para ver qué objeto se está procesando
        print(f"Procesando edad para Ganado ID: {obj.pk}") 
        return obj.edad
    edad.short_description = 'Edad'

    def historial_vacunacion(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse, NoReverseMatch
        
        print(f"Procesando historial_vacunacion para Ganado ID: {obj.pk}") # Añadimos print
        
        vacunaciones = obj.vacunaciones.select_related('vacuna').order_by('-fecha_aplicacion')
        if not vacunaciones.exists():
            return "Sin registros"
        
        html = "<ul>"
        for reg in vacunaciones:
            if hasattr(reg, 'vacuna') and reg.vacuna:
                try:
                    vacuna_link = reverse("admin:inventario_vacuna_change", args=[reg.vacuna.pk])
                    html += f'<li>{reg.fecha_aplicacion}: <a href="{vacuna_link}">{reg.vacuna.nombre}</a></li>'
                except NoReverseMatch:
                    html += f'<li>{reg.fecha_aplicacion}: {reg.vacuna.nombre} (link no disponible)</li>'
            else:
                html += f'<li>{reg.fecha_aplicacion}: Vacuna no encontrada (ID: {reg.vacuna_id})</li>'
        html += "</ul>"
        return format_html(html)
    historial_vacunacion.short_description = 'Historial de Vacunación'

    def proximas_vacunas(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse, NoReverseMatch
        
        print(f"Procesando proximas_vacunas para Ganado ID: {obj.pk}") # Añadimos print

        proximas = obj.vacunaciones.select_related('vacuna').filter(fecha_proxima_dosis__isnull=False).order_by('fecha_proxima_dosis')
        if not proximas.exists():
            return "Ninguna programada"
        
        html = "<ul>"
        for reg in proximas[:3]:
            if hasattr(reg, 'vacuna') and reg.vacuna:
                try:
                    link = reverse("admin:inventario_vacuna_change", args=[reg.vacuna.pk])
                    html += f'<li>{reg.fecha_proxima_dosis}: <a href="{link}">{reg.vacuna.nombre}</a></li>'
                except NoReverseMatch:
                    html += f'<li>{reg.fecha_proxima_dosis}: {reg.vacuna.nombre} (link no disponible)</li>'
            else:
                html += f'<li>{reg.fecha_proxima_dosis}: Vacuna no encontrada (ID: {reg.vacuna_id})</li>'
        html += "</ul>"
        return format_html(html)
    proximas_vacunas.short_description = 'Próximas Vacunas'

@admin.register(Medicamento)
class MedicamentoAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'cantidad_ingresada', 'cantidad_usada', 'cantidad_restante_con_unidad', 'categoria', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_ingreso', 'f_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('categoria', 'ubicaciones', 'proveedores', 'fecha_vencimiento')
    search_fields = ('nombre', 'categoria__nombre', 'ubicaciones__nombre', 'proveedores__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')
    filter_horizontal = ('proveedores', 'ubicaciones')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'ubicaciones', 'proveedores', 'imagen', 'descripcion')
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

    def f_compra(self, obj):
        return obj.fecha_compra
    f_compra.short_description = 'F. Compra'

    def f_ingreso(self, obj):
        return obj.fecha_ingreso
    f_ingreso.short_description = 'F. Ingreso'

    def f_vencimiento(self, obj):
        return obj.fecha_vencimiento
    f_vencimiento.short_description = 'F. Vencimiento'

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        if not proveedores_links:
            return "Sin proveedor"
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'

class VacunaForm(forms.ModelForm):
    etiquetas_padre = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.filter(parent__isnull=True).order_by('nombre'),
        widget=admin.widgets.FilteredSelectMultiple('Etiquetas Padre', is_stacked=False),
        required=False,
        label='Etiquetas Principales'
    )
    sub_etiquetas = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '10'}),
        required=False,
        label='Sub-Etiquetas'
    )

    class Meta:
        model = Vacuna
        exclude = ('etiquetas',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            parent_tags = self.instance.etiquetas.filter(parent__isnull=True)
            self.fields['etiquetas_padre'].initial = parent_tags

            sub_tags = self.instance.etiquetas.filter(parent__isnull=False)
            if parent_tags.exists():
                self.fields['sub_etiquetas'].queryset = Etiqueta.objects.filter(parent__in=parent_tags).order_by('nombre')
            self.fields['sub_etiquetas'].initial = sub_tags

@admin.register(Vacuna)
class VacunaAdmin(ImagenAdminMixin):
    form = VacunaForm
    list_display = ('nombre', 'tipo', 'disponible', 'mostrar_etiquetas', 'cantidad_con_unidad', 'fecha_compra', 'fecha_vencimiento', 'mostrar_proveedores', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('disponible', 'tipo', 'etiquetas', 'fecha_vencimiento', 'proveedores', 'ubicaciones')
    search_fields = ('nombre', 'tipo', 'etiquetas__nombre')
    list_editable = ('disponible',)
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'tipo', 'disponible', 'imagen', 'descripcion')
        }),
        ('Organización', {
            'classes': ('collapse',),
            'fields': ('etiquetas_padre', 'sub_etiquetas')
        }),
        ('Cantidad y Dosis', {
            'fields': (('cantidad', 'unidad_medida'), 'dosis_crecimiento', 'dosis_edad', 'dosis_peso')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
        ('Ubicación y Proveedores', {
            'fields': ('ubicaciones', 'proveedores')
        }),
    )
    
    filter_horizontal = ('proveedores', 'ubicaciones')

    class Media:
        js = ('admin/js/admin_etiquetas.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        parent_tags = form.cleaned_data.get('etiquetas_padre')
        sub_tags = form.cleaned_data.get('sub_etiquetas')

        if parent_tags is not None and sub_tags is not None:
            obj.etiquetas.set(parent_tags | sub_tags)
        elif parent_tags is not None:
            obj.etiquetas.set(parent_tags)
        elif sub_tags is not None:
            obj.etiquetas.set(sub_tags)
        else:
            obj.etiquetas.clear()

    def mostrar_etiquetas(self, obj):
        parent_tags = obj.etiquetas.filter(parent__isnull=True)
        sub_tags = obj.etiquetas.filter(parent__isnull=False)
        
        display_parts = []
        if parent_tags.exists():
            display_parts.append("Principales: " + ", ".join([e.nombre for e in parent_tags]))
        if sub_tags.exists():
            display_parts.append("Sub: " + ", ".join([e.nombre for e in sub_tags]))
            
        return " | ".join(display_parts) if display_parts else "Ninguna"
    mostrar_etiquetas.short_description = 'Etiquetas'

    def cantidad_con_unidad(self, obj):
        return f"{obj.cantidad} {obj.get_unidad_medida_display()}"
    cantidad_con_unidad.short_description = 'Cantidad'

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        if not proveedores_links:
            return "Sin proveedor"
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'

class AlimentoForm(forms.ModelForm):
    etiquetas_padre = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.filter(parent__isnull=True).order_by('nombre'),
        widget=admin.widgets.FilteredSelectMultiple('Etiquetas Padre', is_stacked=False),
        required=False,
        label='Etiquetas Principales'
    )
    sub_etiquetas = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.none(),
        widget=forms.SelectMultiple(attrs={'size': '10'}),
        required=False,
        label='Sub-Etiquetas'
    )

    class Meta:
        model = Alimento
        exclude = ('etiquetas',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            parent_tags = self.instance.etiquetas.filter(parent__isnull=True)
            self.fields['etiquetas_padre'].initial = parent_tags

            sub_tags = self.instance.etiquetas.filter(parent__isnull=False)
            if parent_tags.exists():
                self.fields['sub_etiquetas'].queryset = Etiqueta.objects.filter(parent__in=parent_tags).order_by('nombre')
            self.fields['sub_etiquetas'].initial = sub_tags

@admin.register(Alimento)
class AlimentoAdmin(ImagenAdminMixin):
    form = AlimentoForm
    list_display = ('nombre', 'categoria', 'mostrar_etiquetas', 'cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    
    class Media:
        js = ('admin/js/admin_etiquetas.js',)
    list_filter = ('categoria', 'ubicaciones', 'proveedores', 'fecha_vencimiento', 'etiquetas')
    search_fields = ('nombre', 'categoria__nombre', 'proveedores__nombre', 'etiquetas__nombre')
    readonly_fields = ('cantidad_kg_usada', 'cantidad_kg_restante')
    
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'proveedores', 'ubicaciones', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio (en Kg)', {
            'fields': ('cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'precio')
        }),
        ('Organización', {
            'classes': ('collapse',),
            'fields': ('etiquetas_padre', 'sub_etiquetas')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
    )

    filter_horizontal = ('proveedores', 'ubicaciones')

    def save_model(self, request, obj, form, change):
        # Save the main object first
        super().save_model(request, obj, form, change)

        # Get the selected parent and sub-tags from the form
        parent_tags = form.cleaned_data.get('etiquetas_padre')
        sub_tags = form.cleaned_data.get('sub_etiquetas')

        # Combine the tags and update the ManyToManyField
        if parent_tags is not None and sub_tags is not None:
            obj.etiquetas.set(parent_tags | sub_tags)
        elif parent_tags is not None:
            obj.etiquetas.set(parent_tags)
        elif sub_tags is not None:
            obj.etiquetas.set(sub_tags)
        else:
            obj.etiquetas.clear()

    def cantidad_kg_restante(self, obj):
        return f"{obj.cantidad_kg_ingresada - obj.cantidad_kg_usada} Kg"
    cantidad_kg_restante.short_description = 'Cantidad Restante'

    def mostrar_etiquetas(self, obj):
        parent_tags = obj.etiquetas.filter(parent__isnull=True)
        sub_tags = obj.etiquetas.filter(parent__isnull=False)
        
        display_parts = []
        if parent_tags.exists():
            display_parts.append("Principales: " + ", ".join([e.nombre for e in parent_tags]))
        if sub_tags.exists():
            display_parts.append("Sub: " + ", ".join([e.nombre for e in sub_tags]))
            
        return " | ".join(display_parts) if display_parts else "Ninguna"
    mostrar_etiquetas.short_description = 'Etiquetas'

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        
        if not proveedores_links:
            return "Sin proveedor"
            
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'

@admin.register(ControlPlaga)
class ControlPlagaAdmin(ImagenAdminMixin):
    list_display = ('nombre_producto', 'tipo', 'cantidad_ingresada', 'cantidad_usada', 'cantidad_restante_con_unidad', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('tipo', 'proveedores', 'ubicaciones', 'fecha_vencimiento')
    search_fields = ('nombre_producto', 'tipo', 'ubicaciones__nombre', 'proveedores__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')

    fieldsets = (
        (None, {
            'fields': ('nombre_producto', 'tipo', 'proveedores', 'ubicaciones', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad_ingresada', 'unidad_medida'), 'cantidad_usada', 'cantidad_restante', 'precio')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_vencimiento')
        }),
    )
    
    filter_horizontal = ('proveedores', 'ubicaciones')
    
    def cantidad_ingresada_con_unidad(self, obj):
        return f"{obj.cantidad_ingresada} {obj.get_unidad_medida_display()}"
    cantidad_ingresada_con_unidad.short_description = 'Ingresado'

    def cantidad_usada_con_unidad(self, obj):
        return f"{obj.cantidad_usada} {obj.get_unidad_medida_display()}"
    cantidad_usada_con_unidad.short_description = 'Usado'

    def cantidad_restante_con_unidad(self, obj):
        return f"{obj.cantidad_restante} {obj.get_unidad_medida_display()}"
    cantidad_restante_con_unidad.short_description = 'Restante'

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        if not proveedores_links:
            return "Sin proveedor"
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'

@admin.register(Potrero)
class PotreroAdmin(ImagenAdminMixin):
    list_display = ('nombre', 'area_hectareas', 'empastado', 'fumigado', 'rozado', 'fecha_proximo_empaste', 'fecha_proxima_fumigacion', 'fecha_proximo_rozado', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('empastado', 'fumigado', 'rozado')
    search_fields = ('nombre',)
    list_editable = ('empastado', 'fumigado', 'rozado', 'fecha_proximo_empaste', 'fecha_proxima_fumigacion', 'fecha_proximo_rozado')
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'area_hectareas', 'imagen', 'descripcion')
        }),
        ('Estado Actual y Próximas Acciones', {
            'fields': (('empastado', 'fecha_proximo_empaste'), ('fumigado', 'fecha_proxima_fumigacion'), ('rozado', 'fecha_proximo_rozado'))
        }),
        ('Intercambio de Potreros', {
            'fields': ('intercambio_con_potrero', 'fecha_intercambio')
        }),
    )

@admin.register(Mantenimiento)
class MantenimientoAdmin(ImagenAdminMixin):
    list_display = (
        'equipo', 
        'fecha_ultimo_mantenimiento', 
        'fecha_proximo_mantenimiento', 
        'completado', 
        'mostrar_lugares_mantenimiento', 
        'imagen_thumbnail'
    )
    list_per_page = 10
    list_filter = ('completado', 'fecha_proximo_mantenimiento', 'lugares_mantenimiento')
    search_fields = ('equipo', 'lugares_mantenimiento__nombre_lugar')
    list_editable = ('completado',)
    filter_horizontal = ('lugares_mantenimiento',)
    
    fieldsets = (
        (None, {
            'fields': ('equipo', 'lugares_mantenimiento', 'imagen', 'descripcion')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento', 'completado')
        }),
    )

    def mostrar_lugares_mantenimiento(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        
        lugares_links = []
        for lugar in obj.lugares_mantenimiento.all():
            link = reverse("admin:inventario_lugarmantenimiento_change", args=[lugar.pk])
            lugares_links.append(format_html('<a href="{}">{}</a>', link, lugar.nombre_lugar))
        
        if not lugares_links:
            return "Sin lugar asignado"
            
        return format_html(", ".join(lugares_links))
    mostrar_lugares_mantenimiento.short_description = "Lugares de Mantenimiento"

@admin.register(Combustible)
class CombustibleAdmin(ImagenAdminMixin):
    list_display = ('tipo', 'cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio', 'mostrar_proveedores', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('tipo', 'ubicaciones', 'proveedores')
    search_fields = ('tipo', 'ubicaciones__nombre', 'proveedores__nombre')

    readonly_fields = ('cantidad_galones_usados', 'cantidad_galones_restantes')

    fieldsets = (
        (None, {
            'fields': ('tipo', 'ubicaciones', 'proveedores', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio (en Galones)', {
            'fields': ('cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio')
        }),
    )
    
    filter_horizontal = ('proveedores', 'ubicaciones')

    def cantidad_galones_restantes(self, obj):
        return f"{obj.cantidad_galones_ingresada - obj.cantidad_galones_usados} gal"
    cantidad_galones_restantes.short_description = 'Galones Restantes'

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        if not proveedores_links:
            return "Sin proveedor"
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'

# de acá pa abajo lo nuevo xd 

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "cedula", "correo", "numero")
    search_fields = ("nombre", "apellido", "cedula")
    list_per_page = 10

@admin.register(Dotacion)
class DotacionAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "camisa_franela", "pantalon", "zapato", "fecha_entrega")
    list_per_page = 10
    list_filter = ("camisa_franela", "pantalon", "zapato")
    list_editable = ("camisa_franela", "pantalon", "zapato")

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "valor", "pago_realizado", "metodo_pago", "forma_pago", "fecha_pago")
    list_per_page = 10
    list_filter = ("forma_pago", "pago_realizado")
    search_fields = ("trabajador__nombre", "trabajador__apellido", "trabajador__cedula")
    list_editable = ("pago_realizado",)

@admin.register(LugarMantenimiento)
class LugarMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre_lugar", "nombre_empresa", "mostrar_proveedores", "correo", "numero")
    list_per_page = 10
    search_fields = ("nombre_lugar", "nombre_empresa", "ubicaciones__nombre", "proveedores__nombre")
    list_filter = ("ubicaciones", "proveedores")
    filter_horizontal = ('proveedores', 'ubicaciones')
    
    fieldsets = (
        ('Información del Lugar', {
            'fields': ('nombre_lugar', 'nombre_empresa', 'direccion', 'correo', 'numero', 'descripcion')
        }),
        ('Asignaciones', {
            'fields': ('ubicaciones', 'proveedores')
        }),
    )

    def mostrar_proveedores(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        proveedores_links = []
        for p in obj.proveedores.all():
            link = reverse("admin:caracteristicas_proveedor_change", args=[p.pk])
            proveedores_links.append(format_html('<a href="{}">{}</a>', link, p.nombre))
        if not proveedores_links:
            return "Sin proveedor"
        return format_html(", ".join(proveedores_links))
    mostrar_proveedores.short_description = 'Proveedores'


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
        if 'date_joined' in form.base_fields:
            form.base_fields['date_joined'].label = 'Fecha de registro'
        return form

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
