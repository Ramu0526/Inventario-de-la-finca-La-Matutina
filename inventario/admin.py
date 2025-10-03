from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from caracteristicas.models import Etiqueta
from .models import (
    Producto, Ganado, Medicamento, Alimento, ControlPlaga,
    Potrero, Mantenimiento, Combustible, Trabajador, Dotacion, Pago, LugarMantenimiento,
    Animal, Vacuna, RegistroVacunacion, Comprador, VentaProducto, RegistroMedicamento,
    FechaProduccion
)

def _get_ubicacion_details_html(u):
    if not u:
        return "<p>No especificada</p>"
    
    nombre = u.nombre or "Dato no ingresado"
    barrio = u.barrio or "Dato no ingresado"
    direccion = u.direccion or "Dato no ingresado"
    link_html = f'<a href="{u.link}" target="_blank">Ver en mapa</a>' if u.link else "No hay enlace"
    
    return f"""
        <div class="details-subsection" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <p style="margin: 0;"><strong>{nombre}</strong></p>
            <p style="margin: 2px 0;">{barrio} - {direccion}</p>
            <p style="margin: 0;">{link_html}</p>
        </div>
    """

def _get_proveedor_details_html(p):
    if not p:
        return "<p>No especificado</p>"

    nombre = p.nombre or "Dato no ingresado"
    nombre_local = p.nombre_local or "No especificado"
    correo = p.correo_electronico or "No especificado"
    telefono = p.telefono or "No especificado"
    
    ubicacion_html = _get_ubicacion_details_html(p.ubicacion) if p.ubicacion else "<p>No hay ubicación asociada.</p>"

    return f"""
        <div class="details-subsection" style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <p style="margin: 0;"><strong>{nombre} ({nombre_local})</strong></p>
            <p style="margin: 2px 0;">{correo} - {telefono}</p>
            <div style="padding-left: 15px; margin-top: 5px;">
                {ubicacion_html}
            </div>
        </div>
    """

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
    list_display = ('nombre', 'ver_detalles')
    search_fields = ('nombre',)
    list_per_page = 10

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    def ver_detalles(self, obj):
        nombre = obj.nombre or "Dato aún no ingresado"
        
        # Obtener el ganado asociado a este tipo de animal
        ganado_asociado = Ganado.objects.filter(animal=obj)
        ganado_html = "<ul>" + "".join([f"<li>{g.identificador}</li>" for g in ganado_asociado]) + "</ul>" if ganado_asociado.exists() else "<p>No hay ganado de este tipo.</p>"

        modal_html = f"""
        <div id="modal-animal-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Tipo de Animal: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-animal-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-section">
                        <h4>Información General</h4>
                        <p><strong>Nombre del Tipo:</strong> {nombre}</p>
                    </div>
                    <div class="details-section">
                        <h4>Ganado de este Tipo</h4>
                        {ganado_html}
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-animal-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'ver_detalles')
    search_fields = ('nombre',)
    list_per_page = 10

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    def ver_detalles(self, obj):
        # Obtener productos comprados
        ventas = obj.ventaproducto_set.all()
        productos_html = "<ul>" + "".join([f"<li>{v.producto.nombre} (Valor: ${v.valor_compra:,.2f}, Abono: ${v.valor_abono:,.2f})</li>" for v in ventas]) + "</ul>" if ventas.exists() else "<p>No ha comprado productos.</p>"

        nombre = obj.nombre or "Dato aún no ingresado"
        telefono = obj.telefono or "Dato aún no ingresado"

        # Estructura del modal
        modal_html = f"""
        <div id="modal-comprador-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-comprador-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-section">
                            <h4>Información de Contacto</h4>
                            <p><strong>Nombre:</strong> {nombre}</p>
                            <p><strong>Teléfono:</strong> {telefono}</p>
                        </div>
                        <div class="details-section">
                            <h4>Historial de Compras</h4>
                            {productos_html}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-comprador-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

class FechaProduccionInline(admin.TabularInline):
    model = FechaProduccion
    extra = 1

class VentaProductoInline(admin.TabularInline):
    model = VentaProducto
    extra = 1
    autocomplete_fields = ['comprador']
    fields = ('comprador', 'fecha_venta', 'cantidad_vendida', 'precio_unitario_venta', 'valor_compra', 'valor_abono', 'fecha_produccion_venta')


@admin.register(Producto)
class ProductoAdmin(ImagenAdminMixin):
    # CAMBIA la línea 'list_display' para incluir el estado
    list_display = ('nombre', 'ver_detalles', 'categoria', 'cantidad_con_unidad', 'estado', 'precio', 'precio_total_display', 'imagen_thumbnail')
    list_per_page = 10
    # AÑADE 'estado' a los filtros
    list_filter = ('categoria', 'estado', 'ubicaciones', 'unidad_medida')
    search_fields = ('nombre', 'categoria__nombre')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'ubicaciones', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio', {
            'fields': (('cantidad', 'unidad_medida'), 'precio')
        }),
    )
    
    inlines = [FechaProduccionInline, VentaProductoInline]

    def ver_detalles(self, obj):
        categoria = obj.categoria.nombre if obj.categoria else "Dato aún no ingresado"
        estado = obj.get_estado_display() or "Dato aún no ingresado"
        
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen and hasattr(obj.imagen, 'url') else "No hay imagen"
        descripcion = obj.descripcion or "Sin descripción"

        # New table logic
        ventas = obj.ventaproducto_set.all().select_related('comprador')
        fechas_produccion = obj.fechas_produccion.all()
        
        total_ventas_valor = sum(v.valor_compra for v in ventas if v.valor_compra is not None)

        tabla_html = """
        <style>
            .admin-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .admin-table th, .admin-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .admin-table th { background-color: #f2f2f2; }
            .admin-table tfoot { font-weight: bold; }
        </style>
        <div class="details-section">
            <h4>Historial de Producción y Ventas</h4>
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>Cantidad Vendida</th>
                        <th>Precio Unitario (Venta)</th>
                        <th>Valor Total (Venta)</th>
                        <th>Fecha Producción (Venta)</th>
                        <th>Comprador</th>
                        <th>Fecha de Venta</th>
                    </tr>
                </thead>
                <tbody>
        """

        if ventas.exists():
            for venta in ventas:
                cantidad_display = f"{venta.cantidad_vendida} {obj.get_unidad_medida_display()}" if venta.cantidad_vendida is not None else "N/A"
                precio_unitario_display = f"${venta.precio_unitario_venta:,.2f}" if venta.precio_unitario_venta is not None else "N/A"
                valor_total_display = f"${venta.valor_compra:,.2f}" if venta.valor_compra is not None else "N/A"
                fecha_produccion_display = venta.fecha_produccion_venta.strftime('%d/%m/%Y') if venta.fecha_produccion_venta else "N/A"
                
                tabla_html += f"""
                    <tr>
                        <td>{cantidad_display}</td>
                        <td>{precio_unitario_display}</td>
                        <td>{valor_total_display}</td>
                        <td>{fecha_produccion_display}</td>
                        <td>{venta.comprador.nombre if venta.comprador else 'N/A'}</td>
                        <td>{venta.fecha_venta.strftime('%d/%m/%Y') if venta.fecha_venta else 'N/A'}</td>
                    </tr>
                """
        else:
            # If no sales, show a row with current production info
            fechas_produccion_str = "<br>".join([fp.fecha.strftime('%d/%m/%Y') for fp in fechas_produccion]) if fechas_produccion.exists() else "N/A"
            tabla_html += f"""
                <tr>
                    <td>{obj.cantidad} {obj.get_unidad_medida_display()}</td>
                    <td>${obj.precio:,.2f}</td>
                    <td>${obj.precio_total:,.2f}</td>
                    <td>{fechas_produccion_str}</td>
                    <td colspan="2" style="text-align:center;">Sin ventas registradas</td>
                </tr>
            """

        tabla_html += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="5" style="text-align: right;">Valor Total de Ventas:</td>
                        <td>${total_ventas_valor:,.2f}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """

        modal_html = f"""
        <div id="modal-producto-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content" style="max-width: 80%;">
                <div class="modal-header">
                    <h2>Detalles de Producto: {obj.nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-producto-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-section">
                        <h4>Información General</h4>
                        <p><strong>Categoría:</strong> {categoria} | <strong>Estado:</strong> {estado}</p>
                        <p><strong>Descripción:</strong> {descripcion}</p>
                    </div>
                    {tabla_html}
                    <div class="details-section">
                        <h4>Ubicaciones</h4>
                        {ubicaciones_html}
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-producto-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('identificador', 'ver_detalles', 'animal', 'raza', 'genero', 'peso_kg', 'edad',
                    'crecimiento', 'fecha_nacimiento', 'estado', 'estado_salud',
                    'razon_venta', 'razon_fallecimiento',
                    'peñe', 'historial_vacunacion', 'proximas_vacunas', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('animal', 'genero', 'estado', 'estado_salud', 'crecimiento', 'peñe')
    search_fields = ('identificador', 'animal__nombre', 'raza')
    list_editable = ('estado_salud', 'crecimiento', 'estado')
    
    readonly_fields = ('edad',)

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    fieldsets = (
        ('Información Principal', {
            'fields': ('identificador', 'animal', 'raza', 'genero', 'peso_kg', 'crecimiento', 'imagen', 'descripcion')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_nacimiento', 'edad', 'estado', 'estado_salud')
        }),
        ('Información de Preñez', {
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

    def ver_detalles(self, obj):
        animal = obj.animal.nombre if obj.animal else "Dato aún no ingresado"
        raza = obj.raza or "Dato aún no ingresado"
        genero = obj.get_genero_display() or "Dato aún no ingresado"
        peso = f"{obj.peso_kg} Kg" if obj.peso_kg is not None else "Dato aún no ingresado"
        edad = obj.edad or "Dato aún no ingresado"
        crecimiento = obj.get_crecimiento_display() or "Dato aún no ingresado"
        fecha_nacimiento = obj.fecha_nacimiento.strftime('%d/%m/%Y') if obj.fecha_nacimiento else "Dato aún no ingresado"
        estado = obj.get_estado_display() or "Dato aún no ingresado"
        estado_salud = obj.get_estado_salud_display() or "Dato aún no ingresado"
        
        # Preñez
        preñez = obj.get_peñe_display() or "No aplica"
        fecha_preñez = obj.fecha_peñe.strftime('%d/%m/%Y') if obj.fecha_peñe else "No aplica"
        descripcion_preñez = obj.descripcion_peñe or "No aplica"
        
        # Venta
        fecha_venta = obj.fecha_venta.strftime('%d/%m/%Y') if obj.fecha_venta else "No aplica"
        valor_venta = f"${obj.valor_venta:,.2f}" if obj.valor_venta is not None else "No aplica"
        razon_venta = obj.razon_venta or "No aplica"
        comprador = obj.comprador or "No aplica"
        
        # Fallecimiento
        fecha_fallecimiento = obj.fecha_fallecimiento.strftime('%d/%m/%Y') if obj.fecha_fallecimiento else "No aplica"
        razon_fallecimiento = obj.razon_fallecimiento or "No aplica"
        
        # Historial de vacunación
        vacunaciones = obj.vacunaciones.all()
        vacunaciones_html = "<ul>" + "".join([
            f"<li><strong>{v.vacuna.nombre}</strong> ({v.fecha_aplicacion.strftime('%d/%m/%Y')})<br>"
            f"Próxima dosis: {v.fecha_proxima_dosis.strftime('%d/%m/%Y') if v.fecha_proxima_dosis else 'No programada'}<br>"
            f"Notas: {v.notas or 'Sin notas'}</li>"
            for v in vacunaciones
        ]) + "</ul>" if vacunaciones.exists() else "<p>No hay registros de vacunación.</p>"

        # Historial de medicamentos
        medicamentos = obj.medicamentos_aplicados.all()
        medicamentos_html = "<ul>" + "".join([
            f"<li><strong>{m.medicamento.nombre}</strong> ({m.fecha_aplicacion.strftime('%d/%m/%Y')})<br>"
            f"Notas: {m.notas or 'Sin notas'}</li>"
            for m in medicamentos
        ]) + "</ul>" if medicamentos.exists() else "<p>No hay registros de medicamentos.</p>"

        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen else "No hay imagen"
        descripcion = obj.descripcion or "Sin descripción"

        modal_html = f"""
        <div id="modal-ganado-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de: {obj.identificador}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-ganado-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información Principal</h4>
                                <p><strong>Tipo de Animal:</strong> {animal}</p>
                                <p><strong>Raza:</strong> {raza}</p>
                                <p><strong>Género:</strong> {genero}</p>
                                <p><strong>Peso:</strong> {peso}</p>
                                <p><strong>Edad:</strong> {edad}</p>
                                <p><strong>Crecimiento:</strong> {crecimiento}</p>
                                <p><strong>Fecha de Nacimiento:</strong> {fecha_nacimiento}</p>
                                <p><strong>Estado:</strong> {estado}</p>
                                <p><strong>Estado de Salud:</strong> {estado_salud}</p>
                                <p><strong>Descripción:</strong> {descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Información de Preñez</h4>
                                <p><strong>Tipo de Preñez:</strong> {preñez}</p>
                                <p><strong>Fecha de Preñez:</strong> {fecha_preñez}</p>
                                <p><strong>Descripción:</strong> {descripcion_preñez}</p>
                            </div>
                            <div class="details-section">
                                <h4>Historial de Vacunación</h4>
                                {vacunaciones_html}
                            </div>
                            <div class="details-section">
                                <h4>Historial de Medicamentos</h4>
                                {medicamentos_html}
                            </div>
                            <div class="details-section">
                                <h4>Información de Venta</h4>
                                <p><strong>Fecha de Venta:</strong> {fecha_venta}</p>
                                <p><strong>Valor:</strong> {valor_venta}</p>
                                <p><strong>Razón:</strong> {razon_venta}</p>
                                <p><strong>Comprador:</strong> {comprador}</p>
                            </div>
                            <div class="details-section">
                                <h4>Información de Fallecimiento</h4>
                                <p><strong>Fecha:</strong> {fecha_fallecimiento}</p>
                                <p><strong>Razón:</strong> {razon_fallecimiento}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-ganado-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('nombre', 'ver_detalles', 'cantidad_ingresada', 'cantidad_usada', 'cantidad_restante_con_unidad', 'categoria', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_ingreso', 'f_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('categoria', 'ubicaciones', 'proveedores', 'fecha_vencimiento')
    search_fields = ('nombre', 'categoria__nombre', 'ubicaciones__nombre', 'proveedores__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')
    filter_horizontal = ('proveedores', 'ubicaciones')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
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

    def ver_detalles(self, obj):
        categoria = obj.categoria.nombre if obj.categoria else "Dato aún no ingresado"
        
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"

        imagen_html = "Dato aún no ingresado"
        if obj.imagen and hasattr(obj.imagen, 'url'):
            imagen_html = f'<img src="{obj.imagen.url}" alt="Imagen de {obj.nombre}" class="details-img">'
        
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        fecha_compra = obj.fecha_compra.strftime('%d/%m/%Y') if obj.fecha_compra else "Dato aún no ingresado"
        fecha_ingreso = obj.fecha_ingreso.strftime('%d/%m/%Y') if obj.fecha_ingreso else "Dato aún no ingresado"
        fecha_vencimiento = obj.fecha_vencimiento.strftime('%d/%m/%Y') if obj.fecha_vencimiento else "Dato aún no ingresado"
        precio = f"${obj.precio:,.2f}" if obj.precio is not None else "Dato aún no ingresado"
        cantidad_ingresada = f"{obj.cantidad_ingresada} {obj.get_unidad_medida_display()}" if obj.cantidad_ingresada is not None else "Dato aún no ingresado"
        cantidad_usada = f"{obj.cantidad_usada} {obj.get_unidad_medida_display()}" if obj.cantidad_usada is not None else "Dato aún no ingresado"
        cantidad_restante = f"{obj.cantidad_restante} {obj.get_unidad_medida_display()}" if obj.cantidad_restante is not None else "Dato aún no ingresado"

        modal_html = f"""
        <div id="modal-medicamento-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de: {obj.nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-medicamento-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Categoría:</strong> {categoria}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                                <p><strong>Fecha de Compra:</strong> {fecha_compra}</p>
                                <p><strong>Fecha de Ingreso:</strong> {fecha_ingreso}</p>
                                <p><strong>Fecha de Vencimiento:</strong> {fecha_vencimiento}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Inventario y Precio</h4>
                                <p><strong>Cantidad Ingresada:</strong> {cantidad_ingresada}</p>
                                <p><strong>Cantidad Usada:</strong> {cantidad_usada}</p>
                                <p><strong>Cantidad Restante:</strong> {cantidad_restante}</p>
                                <p><strong>Precio:</strong> {precio}</p>
                            </div>
                            <div class="details-section">
                                <h4>Organización</h4>
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-medicamento-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('nombre', 'ver_detalles', 'tipo', 'disponible', 'mostrar_etiquetas', 'cantidad_con_unidad', 'fecha_compra', 'fecha_vencimiento', 'mostrar_proveedores', 'imagen_thumbnail')
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
        js = ('inventario/js/modalManager.js', 'inventario/js/admin_etiquetas.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
    def ver_detalles(self, obj):
        tipo = obj.tipo or "Dato aún no ingresado"
        disponible = "Sí" if obj.disponible else "No"
        
        etiquetas_html = "<ul>" + "".join([f"<li>{e.nombre}</li>" for e in obj.etiquetas.all()]) + "</ul>" if obj.etiquetas.exists() else "<p>Dato aún no ingresado</p>"
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"
        
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen and hasattr(obj.imagen, 'url') else "No hay imagen"
        descripcion = obj.descripcion or "Sin descripción"
        
        fecha_compra = obj.fecha_compra.strftime('%d/%m/%Y') if obj.fecha_compra else "Dato aún no ingresado"
        fecha_vencimiento = obj.fecha_vencimiento.strftime('%d/%m/%Y') if obj.fecha_vencimiento else "Dato aún no ingresado"
        cantidad = f"{obj.cantidad} {obj.get_unidad_medida_display()}" if obj.cantidad is not None else "Dato aún no ingresado"
        
        dosis_crecimiento = obj.dosis_crecimiento or "No especificada"
        dosis_edad = obj.dosis_edad or "No especificada"
        dosis_peso = obj.dosis_peso or "No especificada"

        modal_html = f"""
        <div id="modal-vacuna-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Vacuna: {obj.nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-vacuna-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Nombre:</strong> {obj.nombre}</p>
                                <p><strong>Tipo:</strong> {tipo}</p>
                                <p><strong>Disponible:</strong> {disponible}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Inventario y Fechas</h4>
                                <p><strong>Cantidad:</strong> {cantidad}</p>
                                <p><strong>Fecha de Compra:</strong> {fecha_compra}</p>
                                <p><strong>Fecha de Vencimiento:</strong> {fecha_vencimiento}</p>
                            </div>
                            <div class="details-section">
                                <h4>Dosis Recomendadas</h4>
                                <p><strong>Por Crecimiento:</strong> {dosis_crecimiento}</p>
                                <p><strong>Por Edad:</strong> {dosis_edad}</p>
                                <p><strong>Por Peso:</strong> {dosis_peso}</p>
                            </div>
                            <div class="details-section">
                                <h4>Organización</h4>
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                                <p><strong>Etiquetas:</strong></p>
                                {etiquetas_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-vacuna-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('nombre', 'ver_detalles','categoria', 'mostrar_etiquetas', 'cantidad_kg_ingresada', 'cantidad_kg_usada', 'cantidad_kg_restante', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    
    class Media:
        js = ('inventario/js/modalManager.js', 'inventario/js/admin_etiquetas.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
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

    def ver_detalles(self, obj):
        # Obtener datos relacionados, manejando casos vacíos
        categoria = obj.categoria.nombre if obj.categoria else "Dato aún no ingresado"
        
        # Formatear listas para mostrarlas como elementos de lista HTML
        etiquetas_html = "<ul>" + "".join([f"<li>{e.nombre}</li>" for e in obj.etiquetas.all()]) + "</ul>" if obj.etiquetas.exists() else "<p>Dato aún no ingresado</p>"
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"

        imagen_html = "Dato aún no ingresado"
        if obj.imagen and hasattr(obj.imagen, 'url'):
            imagen_html = f'<img src="{obj.imagen.url}" alt="Imagen de {obj.nombre}" class="details-img">'
        
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        # Formatear fechas y números
        fecha_compra = obj.fecha_compra.strftime('%d/%m/%Y') if obj.fecha_compra else "Dato aún no ingresado"
        fecha_vencimiento = obj.fecha_vencimiento.strftime('%d/%m/%Y') if obj.fecha_vencimiento else "Dato aún no ingresado"
        precio = f"${obj.precio:,.2f}" if obj.precio is not None else "Dato aún no ingresado"
        cantidad_ingresada = f"{obj.cantidad_kg_ingresada} Kg" if obj.cantidad_kg_ingresada is not None else "Dato aún no ingresado"
        cantidad_usada = f"{obj.cantidad_kg_usada} Kg" if obj.cantidad_kg_usada is not None else "Dato aún no ingresado"
        cantidad_restante = f"{obj.cantidad_kg_restante} Kg" if obj.cantidad_kg_restante is not None else "Dato aún no ingresado"

        # Nueva estructura del modal con diseño mejorado
        modal_html = f"""
        <div id="modal-alimento-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de {obj.nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-alimento-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Categoría:</strong> {categoria}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                                <p><strong>Fecha de Compra:</strong> {fecha_compra}</p>
                                <p><strong>Fecha de Vencimiento:</strong> {fecha_vencimiento}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Inventario y Precio</h4>
                                <p><strong>Cantidad Ingresada:</strong> {cantidad_ingresada}</p>
                                <p><strong>Cantidad Usada:</strong> {cantidad_usada}</p>
                                <p><strong>Cantidad Restante:</strong> {cantidad_restante}</p>
                                <p><strong>Precio:</strong> {precio}</p>
                            </div>
                            <div class="details-section">
                                <h4>Organización</h4>
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                                <p><strong>Etiquetas:</strong></p>
                                {etiquetas_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-alimento-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'


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
    list_display = ('nombre_producto', 'ver_detalles', 'tipo', 'cantidad_ingresada', 'cantidad_usada', 'cantidad_restante_con_unidad', 'precio', 'mostrar_proveedores', 'fecha_compra', 'fecha_vencimiento', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('tipo', 'proveedores', 'ubicaciones', 'fecha_vencimiento')
    search_fields = ('nombre_producto', 'tipo', 'ubicaciones__nombre', 'proveedores__nombre')
    
    readonly_fields = ('cantidad_usada', 'cantidad_restante')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

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
    
    def ver_detalles(self, obj):
        # Formatear listas
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"

        imagen_html = "Dato aún no ingresado"
        if obj.imagen and hasattr(obj.imagen, 'url'):
            imagen_html = f'<img src="{obj.imagen.url}" alt="Imagen de {obj.nombre_producto}" class="details-img">'
        
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        # Formatear fechas y números
        fecha_compra = obj.fecha_compra.strftime('%d/%m/%Y') if obj.fecha_compra else "Dato aún no ingresado"
        fecha_vencimiento = obj.fecha_vencimiento.strftime('%d/%m/%Y') if obj.fecha_vencimiento else "Dato aún no ingresado"
        precio = f"${obj.precio:,.2f}" if obj.precio is not None else "Dato aún no ingresado"
        cantidad_ingresada = f"{obj.cantidad_ingresada} {obj.get_unidad_medida_display()}" if obj.cantidad_ingresada is not None else "Dato aún no ingresado"
        cantidad_usada = f"{obj.cantidad_usada} {obj.get_unidad_medida_display()}" if obj.cantidad_usada is not None else "Dato aún no ingresado"
        cantidad_restante = f"{obj.cantidad_restante} {obj.get_unidad_medida_display()}" if obj.cantidad_restante is not None else "Dato aún no ingresado"

        # Estructura del modal
        modal_html = f"""
        <div id="modal-controlplaga-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de: {obj.nombre_producto}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-controlplaga-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Tipo:</strong> {obj.tipo}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                                <p><strong>Fecha de Compra:</strong> {fecha_compra}</p>
                                <p><strong>Fecha de Vencimiento:</strong> {fecha_vencimiento}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Inventario y Precio</h4>
                                <p><strong>Cantidad Ingresada:</strong> {cantidad_ingresada}</p>
                                <p><strong>Cantidad Usada:</strong> {cantidad_usada}</p>
                                <p><strong>Cantidad Restante:</strong> {cantidad_restante}</p>
                                <p><strong>Precio:</strong> {precio}</p>
                            </div>
                            <div class="details-section">
                                <h4>Organización</h4>
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-controlplaga-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('nombre', 'ver_detalles', 'area_hectareas', 'empastado', 'fumigado', 'rozado', 'fecha_proximo_empaste', 'fecha_proxima_fumigacion', 'fecha_proximo_rozado', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('empastado', 'fumigado', 'rozado')
    search_fields = ('nombre',)
    list_editable = ('empastado', 'fumigado', 'rozado', 'fecha_proximo_empaste', 'fecha_proxima_fumigacion', 'fecha_proximo_rozado')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
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

    def ver_detalles(self, obj):
        nombre = obj.nombre or "Dato aún no ingresado"
        area = f"{obj.area_hectareas} ha" if obj.area_hectareas is not None else "Dato aún no ingresado"
        
        empastado = "Sí" if obj.empastado else "No"
        fumigado = "Sí" if obj.fumigado else "No"
        rozado = "Sí" if obj.rozado else "No"
        
        fecha_empaste = obj.fecha_proximo_empaste.strftime('%d/%m/%Y') if obj.fecha_proximo_empaste else "No programado"
        fecha_fumigacion = obj.fecha_proxima_fumigacion.strftime('%d/%m/%Y') if obj.fecha_proxima_fumigacion else "No programado"
        fecha_rozado = obj.fecha_proximo_rozado.strftime('%d/%m/%Y') if obj.fecha_proximo_rozado else "No programado"
        
        intercambio_potrero = obj.intercambio_con_potrero.nombre if obj.intercambio_con_potrero else "Ninguno"
        fecha_intercambio = obj.fecha_intercambio.strftime('%d/%m/%Y') if obj.fecha_intercambio else "No programado"
        
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen and hasattr(obj.imagen, 'url') else "No hay imagen"
        descripcion = obj.descripcion or "Sin descripción"

        modal_html = f"""
        <div id="modal-potrero-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Potrero: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-potrero-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Nombre:</strong> {nombre}</p>
                                <p><strong>Área:</strong> {area}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Estado y Próximas Acciones</h4>
                                <p><strong>Empastado:</strong> {empastado} (Próximo: {fecha_empaste})</p>
                                <p><strong>Fumigado:</strong> {fumigado} (Próximo: {fecha_fumigacion})</p>
                                <p><strong>Rozado:</strong> {rozado} (Próximo: {fecha_rozado})</p>
                            </div>
                            <div class="details-section">
                                <h4>Intercambio de Potreros</h4>
                                <p><strong>Intercambio con:</strong> {intercambio_potrero}</p>
                                <p><strong>Fecha de Intercambio:</strong> {fecha_intercambio}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-potrero-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

@admin.register(Mantenimiento)
class MantenimientoAdmin(ImagenAdminMixin):
    list_display = (
        'equipo',
        'ver_detalles',
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

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
    fieldsets = (
        (None, {
            'fields': ('equipo', 'lugares_mantenimiento', 'imagen', 'descripcion')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_ultimo_mantenimiento', 'fecha_proximo_mantenimiento', 'completado')
        }),
    )

    def ver_detalles(self, obj):
        equipo = obj.equipo or "Dato aún no ingresado"
        fecha_ultimo = obj.fecha_ultimo_mantenimiento.strftime('%d/%m/%Y') if obj.fecha_ultimo_mantenimiento else "Dato aún no ingresado"
        fecha_proximo = obj.fecha_proximo_mantenimiento.strftime('%d/%m/%Y') if obj.fecha_proximo_mantenimiento else "Dato aún no ingresado"
        completado = "Sí" if obj.completado else "No"
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        lugares_html = "<ul>" + "".join([f"<li>{l.nombre_lugar}</li>" for l in obj.lugares_mantenimiento.all()]) + "</ul>" if obj.lugares_mantenimiento.exists() else "<p>Dato aún no ingresado</p>"
        imagen_html = f'<img src="{obj.imagen.url}" class="details-img">' if obj.imagen else "No hay imagen"

        modal_html = f"""
        <div id="modal-mantenimiento-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Mantenimiento de: {equipo}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-mantenimiento-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Equipo:</strong> {equipo}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Fechas y Estado</h4>
                                <p><strong>Último Mantenimiento:</strong> {fecha_ultimo}</p>
                                <p><strong>Próximo Mantenimiento:</strong> {fecha_proximo}</p>
                                <p><strong>Completado:</strong> {completado}</p>
                            </div>
                            <div class="details-section">
                                <h4>Lugares de Mantenimiento</h4>
                                {lugares_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-mantenimiento-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ('tipo', 'ver_detalles', 'cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio', 'mostrar_proveedores', 'imagen_thumbnail')
    list_per_page = 10
    list_filter = ('tipo', 'ubicaciones', 'proveedores')
    search_fields = ('tipo', 'ubicaciones__nombre', 'proveedores__nombre')

    readonly_fields = ('cantidad_galones_usados', 'cantidad_galones_restantes')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    fieldsets = (
        (None, {
            'fields': ('tipo', 'ubicaciones', 'proveedores', 'imagen', 'descripcion')
        }),
        ('Cantidad y Precio (en Galones)', {
            'fields': ('cantidad_galones_ingresada', 'cantidad_galones_usados', 'cantidad_galones_restantes', 'precio')
        }),
    )
    
    filter_horizontal = ('proveedores', 'ubicaciones')

    def ver_detalles(self, obj):
        # Formatear listas para mostrarlas como elementos de lista HTML
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"

        imagen_html = "Dato aún no ingresado"
        if obj.imagen and hasattr(obj.imagen, 'url'):
            imagen_html = f'<img src="{obj.imagen.url}" alt="Imagen de {obj.tipo}" class="details-img">'
        
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        # Formatear números
        precio = f"${obj.precio:,.2f}" if obj.precio is not None else "Dato aún no ingresado"
        cantidad_ingresada = f"{obj.cantidad_galones_ingresada} gal" if obj.cantidad_galones_ingresada is not None else "Dato aún no ingresado"
        cantidad_usada = f"{obj.cantidad_galones_usados} gal" if obj.cantidad_galones_usados is not None else "Dato aún no ingresado"
        cantidad_restante = f"{obj.cantidad_galones_restantes} gal" if obj.cantidad_galones_restantes is not None else "Dato aún no ingresado"

        # Estructura del modal
        modal_html = f"""
        <div id="modal-combustible-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Combustible: {obj.tipo}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-combustible-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            {imagen_html}
                            <div class="details-section">
                                <h4>Información General</h4>
                                <p><strong>Tipo:</strong> {obj.tipo}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Inventario y Precio</h4>
                                <p><strong>Cantidad Ingresada:</strong> {cantidad_ingresada}</p>
                                <p><strong>Cantidad Usada:</strong> {cantidad_usada}</p>
                                <p><strong>Cantidad Restante:</strong> {cantidad_restante}</p>
                                <p><strong>Precio por Galón:</strong> {precio}</p>
                            </div>
                            <div class="details-section">
                                <h4>Organización</h4>
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-combustible-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
    list_display = ("nombre", "ver_detalles", "apellido", "cedula", "correo", "numero")
    search_fields = ("nombre", "apellido", "cedula")
    list_per_page = 10

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    def ver_detalles(self, obj):
        nombre = f"{obj.nombre} {obj.apellido}" or "Dato aún no ingresado"
        cedula = obj.cedula or "Dato aún no ingresado"
        correo = obj.correo or "Dato aún no ingresado"
        numero = obj.numero or "Dato aún no ingresado"
        
        # Historial de dotaciones
        dotaciones = obj.dotaciones.all().order_by('-fecha_entrega')
        dotaciones_html = "<ul>" + "".join([f"<li>Fecha: {d.fecha_entrega.strftime('%d/%m/%Y')} (Camisa: {'Sí' if d.camisa_franela else 'No'}, Pantalón: {'Sí' if d.pantalon else 'No'}, Zapatos: {'Sí' if d.zapato else 'No'})</li>" for d in dotaciones]) + "</ul>" if dotaciones.exists() else "<p>Sin historial de dotaciones.</p>"
        
        # Historial de pagos
        pagos = obj.pagos.all().order_by('-fecha_pago')
        pagos_html = "<ul>" + "".join([f"<li>Fecha: {p.fecha_pago.strftime('%d/%m/%Y')} - Valor: ${p.valor:,.2f} ({'Pagado' if p.pago_realizado else 'Pendiente'})</li>" for p in pagos]) + "</ul>" if pagos.exists() else "<p>Sin historial de pagos.</p>"

        modal_html = f"""
        <div id="modal-trabajador-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Trabajador: {nombre}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-trabajador-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            <div class="details-section">
                                <h4>Información Personal</h4>
                                <p><strong>Nombre Completo:</strong> {nombre}</p>
                                <p><strong>Cédula:</strong> {cedula}</p>
                                <p><strong>Correo:</strong> {correo}</p>
                                <p><strong>Número de Contacto:</strong> {numero}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Historial de Dotaciones</h4>
                                {dotaciones_html}
                            </div>
                            <div class="details-section">
                                <h4>Historial de Pagos</h4>
                                {pagos_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-trabajador-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

@admin.register(Dotacion)
class DotacionAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "ver_detalles", "camisa_franela", "pantalon", "zapato", "fecha_entrega")
    list_per_page = 10
    list_filter = ("camisa_franela", "pantalon", "zapato")
    list_editable = ("camisa_franela", "pantalon", "zapato")

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    def ver_detalles(self, obj):
        trabajador_info = f"{obj.trabajador.nombre} {obj.trabajador.apellido} (C.C: {obj.trabajador.cedula})" if obj.trabajador else "Dato aún no ingresado"
        
        # Formatear booleans
        camisa = "Sí" if obj.camisa_franela else "No"
        pantalon = "Sí" if obj.pantalon else "No"
        zapato = "Sí" if obj.zapato else "No"
        
        # Formatear fecha
        fecha_entrega = obj.fecha_entrega.strftime('%d/%m/%Y') if obj.fecha_entrega else "Dato aún no ingresado"

        # Estructura del modal
        modal_html = f"""
        <div id="modal-dotacion-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Dotación para: {obj.trabajador.nombre} {obj.trabajador.apellido}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-dotacion-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-section">
                        <h4>Información del Trabajador</h4>
                        <p><strong>Trabajador:</strong> {trabajador_info}</p>
                    </div>
                    <div class="details-section">
                        <h4>Detalles de la Dotación</h4>
                        <p><strong>Camisa/Franela:</strong> {camisa}</p>
                        <p><strong>Pantalón:</strong> {pantalon}</p>
                        <p><strong>Zapatos:</strong> {zapato}</p>
                        <p><strong>Fecha de Entrega:</strong> {fecha_entrega}</p>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-dotacion-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("trabajador", 'ver_detalles', "valor", "pago_realizado", "metodo_pago", "forma_pago", "fecha_pago")
    list_per_page = 10
    list_filter = ("forma_pago", "pago_realizado")
    search_fields = ("trabajador__nombre", "trabajador__apellido", "trabajador__cedula")
    list_editable = ("pago_realizado",)

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }

    def ver_detalles(self, obj):
        trabajador_info = f"{obj.trabajador.nombre} {obj.trabajador.apellido} (C.C: {obj.trabajador.cedula})" if obj.trabajador else "Dato aún no ingresado"
        valor = f"${obj.valor:,.2f}" if obj.valor is not None else "Dato aún no ingresado"
        pago_realizado = "Sí" if obj.pago_realizado else "No"
        metodo_pago = obj.metodo_pago or "Dato aún no ingresado"
        forma_pago = obj.get_forma_pago_display() or "Dato aún no ingresado"
        fecha_pago = obj.fecha_pago.strftime('%d/%m/%Y') if obj.fecha_pago else "Dato aún no ingresado"

        modal_html = f"""
        <div id="modal-pago-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de Pago para: {obj.trabajador.nombre} {obj.trabajador.apellido}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-pago-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-section">
                        <h4>Información del Trabajador</h4>
                        <p><strong>Trabajador:</strong> {trabajador_info}</p>
                    </div>
                    <div class="details-section">
                        <h4>Detalles del Pago</h4>
                        <p><strong>Valor del Pago:</strong> {valor}</p>
                        <p><strong>¿Pago Realizado?:</strong> {pago_realizado}</p>
                        <p><strong>Método de Pago:</strong> {metodo_pago}</p>
                        <p><strong>Forma de Pago:</strong> {forma_pago}</p>
                        <p><strong>Fecha de Pago:</strong> {fecha_pago}</p>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-pago-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

@admin.register(LugarMantenimiento)
class LugarMantenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre_lugar", "ver_detalles", "nombre_empresa", "mostrar_proveedores", "correo", "numero")
    list_per_page = 10
    search_fields = ("nombre_lugar", "nombre_empresa", "ubicaciones__nombre", "proveedores__nombre")
    list_filter = ("ubicaciones", "proveedores")
    filter_horizontal = ('proveedores', 'ubicaciones')

    class Media:
        js = ('inventario/js/modalManager.js',)
        css = {
            'all': ('inventario/css/StyleModal.css',)
        }
    
    fieldsets = (
        ('Información del Lugar', {
            'fields': ('nombre_lugar', 'nombre_empresa', 'direccion', 'correo', 'numero', 'descripcion')
        }),
        ('Asignaciones', {
            'fields': ('ubicaciones', 'proveedores')
        }),
    )

    def ver_detalles(self, obj):
        nombre_lugar = obj.nombre_lugar or "Dato aún no ingresado"
        nombre_empresa = obj.nombre_empresa or "Dato aún no ingresado"
        direccion = obj.direccion or "Dato aún no ingresado"
        correo = obj.correo or "Dato aún no ingresado"
        numero = obj.numero or "Dato aún no ingresado"
        descripcion = obj.descripcion or "Dato aún no ingresado"
        
        ubicaciones_html = "".join([_get_ubicacion_details_html(u) for u in obj.ubicaciones.all()]) if obj.ubicaciones.exists() else "<p>Dato aún no ingresado</p>"
        proveedores_html = "".join([_get_proveedor_details_html(p) for p in obj.proveedores.all()]) if obj.proveedores.exists() else "<p>Dato aún no ingresado</p>"

        modal_html = f"""
        <div id="modal-lugarmantenimiento-{obj.pk}" class="modal" style="display:none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Detalles de: {nombre_lugar}</h2>
                    <span class="close-btn" onclick="document.getElementById('modal-lugarmantenimiento-{obj.pk}').style.display='none'">&times;</span>
                </div>
                <hr class="separator">
                <div class="modal-body">
                    <div class="details-grid">
                        <div class="details-left-column">
                            <div class="details-section">
                                <h4>Información del Lugar</h4>
                                <p><strong>Nombre del Lugar:</strong> {nombre_lugar}</p>
                                <p><strong>Nombre de la Empresa:</strong> {nombre_empresa}</p>
                                <p><strong>Dirección:</strong> {direccion}</p>
                                <p><strong>Correo:</strong> {correo}</p>
                                <p><strong>Número:</strong> {numero}</p>
                                <p><strong>Descripción:</strong></p>
                                <p>{descripcion}</p>
                            </div>
                        </div>
                        <div class="details-right-column">
                            <div class="details-section">
                                <h4>Asignaciones</h4>
                                <p><strong>Ubicaciones:</strong></p>
                                {ubicaciones_html}
                                <p><strong>Proveedores:</strong></p>
                                {proveedores_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <button class="button" onclick="event.preventDefault(); event.stopPropagation(); document.getElementById('modal-lugarmantenimiento-{obj.pk}').style.display='block'">Ver</button>
        """
        return mark_safe(modal_html)
    ver_detalles.short_description = 'Detalles'

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
