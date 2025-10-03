# inventario/views.py
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Alimento, Combustible, ControlPlaga, Ganado, Mantenimiento, Medicamento, Potrero, Animal, VentaProducto, RegistroMedicamento
from caracteristicas.models import Etiqueta, Categoria, Proveedor, Ubicacion
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from .models import Comprador
from .models import Vacuna, RegistroVacunacion, FechaProduccion
from django.utils import timezone
from dateutil.relativedelta import relativedelta


from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.contenttypes.models import ContentType

# --- FUNCIÓN AUXILIAR NUEVA PARA CREAR REGISTROS EN EL HISTORIAL ---
def log_user_action(request, obj, action_flag, message):
    """
    Crea una entrada en el historial (LogEntry) para una acción específica.
    """
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message
    )

def get_safe_image_url(image_field):
    """
    Safely gets the image URL from a CloudinaryField.
    Returns None if the image does not exist or if there's an error generating the URL.
    """
    if not image_field:
        return None
    try:
        return image_field.url
    except Exception:
        # Could log the error here if needed
        return None

def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('user_redirect')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('user_redirect')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    form = AuthenticationForm()
    return render(request, 'inventario/login.html', {'form': form})

@login_required
def lista_productos(request):
    # This view now only handles the initial page load.
    # The modals will be populated by their own dedicated views.
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()
    animales = Animal.objects.all()
    ubicaciones = Ubicacion.objects.all()
    lugares_mantenimiento = LugarMantenimiento.objects.all()

    context = {
        'categorias': categorias,
        'proveedores': proveedores,
        'animales': animales,
        'ubicaciones': ubicaciones,
        'ganado_crecimiento_choices': Ganado.Crecimiento.choices,
        'ganado_estado_choices': Ganado.EstadoAnimal.choices,
        'ganado_estado_salud_choices': Ganado.EstadoSalud.choices,
        'ganado_preñez_choices': Ganado.TipoPrenez.choices,
        'lugares_mantenimiento': lugares_mantenimiento,
        'producto_estado_choices': Producto.EstadoProducto.choices,
    }
    return render(request, 'inventario/lista_productos.html', context)

@login_required
def lista_alimentos(request):
    alimentos_list = Alimento.objects.select_related('categoria').prefetch_related('proveedores', 'ubicaciones').order_by('nombre')

    # Filtros existentes
    nombre_query = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor', '')
    
    # Nuevos filtros
    disponibilidad = request.GET.get('disponibilidad')
    ubicacion_id = request.GET.get('ubicacion')
    vencimiento = request.GET.get('vencimiento')

    if nombre_query:
        alimentos_list = alimentos_list.filter(nombre__icontains=nombre_query)
    if categoria_id:
        alimentos_list = alimentos_list.filter(categoria__id=categoria_id)
    if proveedor_id:
        alimentos_list = alimentos_list.filter(proveedores__id=proveedor_id)
    
    # Lógica para nuevos filtros
    if disponibilidad == 'disponible':
        alimentos_list = alimentos_list.filter(cantidad_kg_ingresada__gt=F('cantidad_kg_usada'))
    elif disponibilidad == 'agotado':
        alimentos_list = alimentos_list.filter(cantidad_kg_ingresada__lte=F('cantidad_kg_usada'))

    if ubicacion_id:
        alimentos_list = alimentos_list.filter(ubicaciones__id=ubicacion_id)

    if vencimiento:
        today = timezone.now().date()
        if vencimiento == '1_semana':
            end_date = today + relativedelta(weeks=1)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '1_mes':
            end_date = today + relativedelta(months=1)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '3_meses':
            end_date = today + relativedelta(months=3)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '6_meses':
            end_date = today + relativedelta(months=6)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '1_ano':
            end_date = today + relativedelta(years=1)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == 'mas_1_ano':
            end_date = today + relativedelta(years=1)
            alimentos_list = alimentos_list.filter(fecha_vencimiento__gt=end_date)

    try:
        items_per_page = int(request.GET.get('items_per_page', 8))
    except (ValueError, TypeError):
        items_per_page = 8

    paginator = Paginator(alimentos_list, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        alimentos_data = []
        for alimento in page_obj.object_list:
            alimentos_data.append({
                'id': alimento.id,
                'nombre': alimento.nombre,
                'cantidad_kg_ingresada': str(alimento.cantidad_kg_ingresada),
                'imagen_url': get_safe_image_url(alimento.imagen),
            })
        
        return JsonResponse({
            'items': alimentos_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def user_redirect(request):
    print("Redirecting to lista_productos")
    return redirect('lista_productos')

@login_required
def alimento_detalles_json(request, alimento_id):
    alimento = get_object_or_404(Alimento, pk=alimento_id)

    etiquetas_del_alimento = list(alimento.etiquetas.values('id', 'nombre', 'parent_id'))
    todas_las_etiquetas_principales = list(Etiqueta.objects.filter(parent__isnull=True).values('id', 'nombre'))
    todas_las_categorias = list(Categoria.objects.values('id', 'nombre'))
    
    proveedores_data = []
    for proveedor in alimento.proveedores.all():
        proveedores_data.append({
            'nombre': proveedor.nombre,
            'nombre_local': getattr(proveedor, 'nombre_local', ''),
            'correo': getattr(proveedor, 'correo_electronico', ''),
            'telefono': getattr(proveedor, 'telefono', ''),
            'imagen_url': get_safe_image_url(getattr(proveedor, 'imagen', None))
        })

    ubicaciones_data = []
    for ubicacion in alimento.ubicaciones.all():
        ubicaciones_data.append({
            'nombre': ubicacion.nombre, 'barrio': ubicacion.barrio,
            'direccion': ubicacion.direccion, 'link': ubicacion.link,
            'imagen_url': get_safe_image_url(getattr(ubicacion, 'imagen', None))
        })
    
    estado = "Disponible" if alimento.cantidad_kg_restante > 0 else "Agotado"

    data = {
        'id': alimento.id,
        'nombre': alimento.nombre,
        'cantidad_ingresada': str(alimento.cantidad_kg_ingresada),
        'cantidad_usada': str(alimento.cantidad_kg_usada),
        'cantidad_restante': str(alimento.cantidad_kg_restante),
        'precio': str(alimento.precio),
        'estado': estado,
        'fecha_compra': alimento.fecha_compra.strftime('%d/%m/%Y'),
        'fecha_vencimiento': alimento.fecha_vencimiento.strftime('%d/%m/%Y'),
        'descripcion': alimento.descripcion or "No hay descripción.", # AÑADE ESTA LÍNEA
        'imagen_url': get_safe_image_url(alimento.imagen),
        'categoria': { 'id': alimento.categoria.id, 'nombre': alimento.categoria.nombre } if alimento.categoria else None,
        'proveedores': proveedores_data,
        'ubicaciones': ubicaciones_data,
        'etiquetas': etiquetas_del_alimento,
        'todas_las_etiquetas_principales': todas_las_etiquetas_principales,
        'todas_las_categorias': todas_las_categorias,
    }
    return JsonResponse(data)

@require_POST
@login_required
def actualizar_ganado_ajax(request):
    try:
        data = json.loads(request.body)
        ganado_id = data.get('ganado_id')
        ganado = get_object_or_404(Ganado, pk=ganado_id)

        # Campos existentes
        ganado.peso_kg = data.get('peso_kg', ganado.peso_kg)
        ganado.estado = data.get('estado', ganado.estado)
        ganado.estado_salud = data.get('estado_salud', ganado.estado_salud)
        ganado.peñe = data.get('preñez', ganado.peñe)
        ganado.descripcion = data.get('descripcion', ganado.descripcion)

        # Nuevos campos
        ganado.crecimiento = data.get('crecimiento', ganado.crecimiento)
        ganado.fecha_peñe = data.get('fecha_preñez') or None
        ganado.descripcion_peñe = data.get('descripcion_preñez', ganado.descripcion_preñe)
        
        # Campos condicionales
        if ganado.estado == 'FALLECIDO':
            ganado.fecha_fallecimiento = data.get('fecha_fallecimiento') or None
            ganado.razon_fallecimiento = data.get('razon_fallecimiento', ganado.razon_fallecimiento)
        else:
            ganado.fecha_fallecimiento = None
            ganado.razon_fallecimiento = None

        if ganado.estado == 'VENDIDO':
            ganado.fecha_venta = data.get('fecha_venta') or None
            ganado.valor_venta = Decimal(data.get('valor_venta')) if data.get('valor_venta') else None
            ganado.razon_venta = data.get('razon_venta', ganado.razon_venta)
            ganado.comprador = data.get('comprador', ganado.comprador)
            ganado.comprador_telefono = data.get('comprador_telefono', ganado.comprador_telefono)
        else:
            ganado.fecha_venta = None
            ganado.valor_venta = None
            ganado.razon_venta = None
            ganado.comprador = None
            ganado.comprador_telefono = None

        ganado.save()

        log_user_action(request, ganado, CHANGE, "Datos del ganado actualizados desde el panel de usuario.")
        return JsonResponse({'status': 'success', 'message': 'Datos del ganado actualizados.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def actualizar_cantidad_alimento(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        cantidad_a_usar = Decimal(data.get('cantidad_a_usar'))
        alimento = get_object_or_404(Alimento, pk=alimento_id)
        if cantidad_a_usar <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor a cero.'}, status=400)
        if cantidad_a_usar > alimento.cantidad_kg_restante:
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente cantidad en inventario.'}, status=400)
        
        alimento.cantidad_kg_usada += cantidad_a_usar
        alimento.save()
        
        # AÑADIDO: Registrar en el historial
        log_user_action(request, alimento, CHANGE, f"Usó {cantidad_a_usar} Kg desde el panel de usuario.")

        return JsonResponse({
            'status': 'success', 'message': 'Cantidad actualizada correctamente.',
            'nueva_cantidad_usada': alimento.cantidad_kg_usada,
            'nueva_cantidad_restante': alimento.cantidad_kg_restante,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def lista_combustibles(request):
    combustibles_list = Combustible.objects.prefetch_related('proveedores', 'ubicaciones').order_by('tipo')

    nombre_query = request.GET.get('nombre', '')
    proveedor_id = request.GET.get('proveedor', '')
    ubicacion_id = request.GET.get('ubicacion', '')

    if nombre_query:
        combustibles_list = combustibles_list.filter(tipo__icontains=nombre_query)
    if proveedor_id:
        combustibles_list = combustibles_list.filter(proveedores__id=proveedor_id)
    if ubicacion_id:
        combustibles_list = combustibles_list.filter(ubicaciones__id=ubicacion_id)

    try:
        items_per_page = int(request.GET.get('items_per_page', 8))
    except (ValueError, TypeError):
        items_per_page = 8

    paginator = Paginator(combustibles_list, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        combustibles_data = []
        for combustible in page_obj.object_list:
            combustibles_data.append({
                'id': combustible.id,
                'tipo': combustible.tipo,
                'cantidad_galones_ingresada': str(combustible.cantidad_galones_ingresada),
                'imagen_url': get_safe_image_url(combustible.imagen),
            })
        
        return JsonResponse({
            'items': combustibles_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def combustible_detalles_json(request, combustible_id):
    combustible = get_object_or_404(Combustible, pk=combustible_id)

    proveedores_data = []
    for proveedor in combustible.proveedores.all():
        proveedores_data.append({
            'nombre': proveedor.nombre,
            'nombre_local': getattr(proveedor, 'nombre_local', ''),
            'correo': getattr(proveedor, 'correo_electronico', ''),
            'telefono': getattr(proveedor, 'telefono', ''),
            'imagen_url': get_safe_image_url(getattr(proveedor, 'imagen', None))
        })

    ubicaciones_data = []
    for ubicacion in combustible.ubicaciones.all():
        ubicaciones_data.append({
            'nombre': ubicacion.nombre, 'barrio': ubicacion.barrio,
            'direccion': ubicacion.direccion, 'link': ubicacion.link,
            'imagen_url': get_safe_image_url(getattr(ubicacion, 'imagen', None))
        })

    data = {
        'id': combustible.id,
        'tipo': combustible.tipo,
        'cantidad_galones_ingresada': str(combustible.cantidad_galones_ingresada),
        'cantidad_galones_usados': str(combustible.cantidad_galones_usados),
        'cantidad_galones_restantes': str(combustible.cantidad_galones_restantes),
        'precio': str(combustible.precio),
        'proveedores': proveedores_data,
        'ubicaciones': ubicaciones_data,
        'descripcion': combustible.descripcion or "No hay descripción.", # AÑADE ESTA LÍNEA
        'imagen_url': get_safe_image_url(combustible.imagen),
    }
    return JsonResponse(data)

@require_POST
@login_required
def actualizar_cantidad_combustible(request):
    try:
        data = json.loads(request.body)
        combustible_id = data.get('combustible_id')
        cantidad_a_usar = Decimal(data.get('cantidad_a_usar'))
        combustible = get_object_or_404(Combustible, pk=combustible_id)
        if cantidad_a_usar <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor a cero.'}, status=400)
        if cantidad_a_usar > combustible.cantidad_galones_restantes:
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente cantidad en inventario.'}, status=400)
        combustible.cantidad_galones_usados += cantidad_a_usar
        combustible.save()
        return JsonResponse({
            'status': 'success', 'message': 'Cantidad actualizada correctamente.',
            'nueva_cantidad_usada': combustible.cantidad_galones_usados,
            'nueva_cantidad_restante': combustible.cantidad_galones_restantes,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def anadir_stock_combustible(request):
    try:
        data = json.loads(request.body)
        combustible_id = data.get('combustible_id')
        cantidad_a_anadir = Decimal(data.get('cantidad_a_anadir'))
        
        if not isinstance(cantidad_a_anadir, Decimal) or cantidad_a_anadir <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser un número positivo.'}, status=400)

        combustible = get_object_or_404(Combustible, pk=combustible_id)
        combustible.cantidad_galones_ingresada += cantidad_a_anadir
        combustible.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Stock añadido correctamente.',
            'nueva_cantidad_ingresada': combustible.cantidad_galones_ingresada,
            'nueva_cantidad_restante': combustible.cantidad_galones_restantes,
        })
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def gestionar_etiqueta_alimento(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        etiqueta_id = data.get('etiqueta_id')
        accion = data.get('accion')
        alimento = get_object_or_404(Alimento, pk=alimento_id)
        etiqueta = get_object_or_404(Etiqueta, pk=etiqueta_id)
        if accion == 'add':
            alimento.etiquetas.add(etiqueta)
            message = 'Etiqueta añadida.'
        elif accion == 'remove':
            alimento.etiquetas.remove(etiqueta)
            message = 'Etiqueta eliminada.'
        else:
            return JsonResponse({'status': 'error', 'message': 'Acción no válida.'}, status=400)
        etiquetas_actualizadas = list(alimento.etiquetas.values('id', 'nombre'))
        return JsonResponse({'status': 'success', 'message': message, 'etiquetas': etiquetas_actualizadas})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@staff_member_required
def get_sub_etiquetas(request):
    parent_ids_str = request.GET.get('parent_ids')
    if not parent_ids_str:
        return JsonResponse({}, status=400)

    try:
        parent_ids = [int(id) for id in parent_ids_str.split(',')]
        sub_etiquetas = Etiqueta.objects.filter(parent__id__in=parent_ids).order_by('nombre')
        data = {etiqueta.id: etiqueta.nombre for etiqueta in sub_etiquetas}
        return JsonResponse(data)
    except (ValueError, TypeError):
        return JsonResponse({}, status=400)

@require_POST
@login_required
def anadir_stock_alimento(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        cantidad_a_anadir = Decimal(data.get('cantidad_a_anadir'))
        if not isinstance(cantidad_a_anadir, Decimal) or cantidad_a_anadir <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser un número positivo.'}, status=400)

        alimento = get_object_or_404(Alimento, pk=alimento_id)
        alimento.cantidad_kg_ingresada += cantidad_a_anadir
        alimento.save()

        # AÑADIDO: Registrar en el historial
        log_user_action(request, alimento, CHANGE, f"Añadió {cantidad_a_anadir} Kg de stock desde el panel de usuario.")

        return JsonResponse({
            'status': 'success',
            'message': 'Stock añadido correctamente.',
            'nueva_cantidad_ingresada': alimento.cantidad_kg_ingresada,
            'nueva_cantidad_restante': alimento.cantidad_kg_restante,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@require_POST
@login_required
def crear_etiqueta_ajax(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        nombre_etiqueta = data.get('nombre_etiqueta', '').strip()
        parent_id = data.get('parent_id', None)

        if not nombre_etiqueta:
            return JsonResponse({'status': 'error', 'message': 'El nombre de la etiqueta no puede estar vacío.'}, status=400)

        alimento = get_object_or_404(Alimento, pk=alimento_id)
        
        if Etiqueta.objects.filter(nombre__iexact=nombre_etiqueta).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe una etiqueta con este nombre.'}, status=400)

        parent_etiqueta = None
        if parent_id:
            parent_etiqueta = get_object_or_404(Etiqueta, pk=parent_id)

        nueva_etiqueta = Etiqueta.objects.create(nombre=nombre_etiqueta, parent=parent_etiqueta)
        alimento.etiquetas.add(nueva_etiqueta)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Etiqueta creada y añadida correctamente. Refrescando detalles...',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def asignar_categoria_ajax(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        categoria_id = data.get('categoria_id')

        if not categoria_id:
            return JsonResponse({'status': 'error', 'message': 'Debe seleccionar una categoría.'}, status=400)

        alimento = get_object_or_404(Alimento, pk=alimento_id)
        categoria = get_object_or_404(Categoria, pk=categoria_id)

        alimento.categoria = categoria
        alimento.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Categoría asignada correctamente. Refrescando detalles...',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def crear_categoria_ajax(request):
    try:
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        nombre_categoria = data.get('nombre_categoria', '').strip()

        if not nombre_categoria:
            return JsonResponse({'status': 'error', 'message': 'El nombre de la categoría no puede estar vacío.'}, status=400)

        alimento = get_object_or_404(Alimento, pk=alimento_id)
        
        if Categoria.objects.filter(nombre__iexact=nombre_categoria).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe una categoría con este nombre.'}, status=400)

        nueva_categoria = Categoria.objects.create(nombre=nombre_categoria)
        alimento.categoria = nueva_categoria
        alimento.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Categoría creada y asignada correctamente. Refrescando detalles...',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def lista_control_plagas(request):
    items_list = ControlPlaga.objects.order_by('nombre_producto')
    
    nombre_query = request.GET.get('nombre', '')
    ubicacion_id = request.GET.get('ubicacion')
    tipo_query = request.GET.get('tipo')
    disponibilidad = request.GET.get('disponibilidad')
    vencimiento = request.GET.get('vencimiento')

    if nombre_query:
        items_list = items_list.filter(nombre_producto__icontains=nombre_query)
    if ubicacion_id:
        items_list = items_list.filter(ubicaciones__id=ubicacion_id)
    if tipo_query:
        items_list = items_list.filter(tipo__icontains=tipo_query)
    
    if disponibilidad == 'disponible':
        items_list = items_list.filter(cantidad_ingresada__gt=F('cantidad_usada'))
    elif disponibilidad == 'agotado':
        items_list = items_list.filter(cantidad_ingresada__lte=F('cantidad_usada'))

    if vencimiento:
        today = timezone.now().date()
        if vencimiento == '1_semana':
            end_date = today + relativedelta(weeks=1)
            items_list = items_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '1_mes':
            end_date = today + relativedelta(months=1)
            items_list = items_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '3_meses':
            end_date = today + relativedelta(months=3)
            items_list = items_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '6_meses':
            end_date = today + relativedelta(months=6)
            items_list = items_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == '1_ano':
            end_date = today + relativedelta(years=1)
            items_list = items_list.filter(fecha_vencimiento__range=[today, end_date])
        elif vencimiento == 'mas_1_ano':
            end_date = today + relativedelta(years=1)
            items_list = items_list.filter(fecha_vencimiento__gt=end_date)

    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.nombre_producto,
            'detalle': f"Quedan: {item.cantidad_restante} {item.get_unidad_medida_display()}",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]
        
        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_ganado(request):
    items_list = Ganado.objects.select_related('animal').order_by('identificador')

    nombre_query = request.GET.get('nombre', '')
    animal_id = request.GET.get('animal', '')
    raza_query = request.GET.get('raza')
    peso_query = request.GET.get('peso')
    crecimiento_query = request.GET.get('crecimiento')
    estado_query = request.GET.get('estado')
    estado_salud_query = request.GET.get('estado_salud')
    preñez_query = request.GET.get('preñez')

    if nombre_query:
        items_list = items_list.filter(identificador__icontains=nombre_query)
    if animal_id:
        items_list = items_list.filter(animal__id=animal_id)
    if raza_query:
        items_list = items_list.filter(raza__icontains=raza_query)
    if crecimiento_query:
        items_list = items_list.filter(crecimiento=crecimiento_query)
    if estado_query:
        items_list = items_list.filter(estado=estado_query)
    if estado_salud_query:
        items_list = items_list.filter(estado_salud=estado_salud_query)
    if preñez_query:
    # Usamos el parámetro 'preñez' para filtrar el campo 'peñe' del modelo
        items_list = items_list.filter(peñe=preñez_query)

    if peso_query:
        if peso_query == '0_10':
            items_list = items_list.filter(peso_kg__lt=10)
        elif peso_query == '10_100':
            items_list = items_list.filter(peso_kg__gte=10, peso_kg__lt=100)
        elif peso_query == '100_250':
            items_list = items_list.filter(peso_kg__gte=100, peso_kg__lt=250)
        elif peso_query == '250_500':
            items_list = items_list.filter(peso_kg__gte=250, peso_kg__lt=500)
        elif peso_query == '500_1000':
            items_list = items_list.filter(peso_kg__gte=500, peso_kg__lt=1000)
        elif peso_query == '1000_mas':
            items_list = items_list.filter(peso_kg__gte=1000)

    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.identificador,
            'detalle': f"{item.animal.nombre if item.animal else 'N/A'} - {item.get_estado_display()}",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]

        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_mantenimientos(request):
    items_list = Mantenimiento.objects.order_by('equipo')

    nombre_query = request.GET.get('nombre', '')
    completado_query = request.GET.get('completado')
    lugar_id = request.GET.get('lugar_mantenimiento')

    if nombre_query:
        items_list = items_list.filter(equipo__icontains=nombre_query)
    
    if completado_query in ['true', 'false']:
        items_list = items_list.filter(completado=(completado_query == 'true'))
            
    if lugar_id:
        items_list = items_list.filter(lugares_mantenimiento__id=lugar_id)

    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.equipo,
            'detalle': f"Próximo: {item.fecha_proximo_mantenimiento.strftime('%d/%m/%Y')}",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]
        
        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_medicamentos(request):
    items_list = Medicamento.objects.select_related('categoria').prefetch_related('proveedores', 'ubicaciones').order_by('nombre')
    
    nombre_query = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor')
    ubicacion_id = request.GET.get('ubicacion')
    disponibilidad = request.GET.get('disponibilidad')

    if nombre_query:
        items_list = items_list.filter(nombre__icontains=nombre_query)
    if categoria_id:
        items_list = items_list.filter(categoria__id=categoria_id)
    if proveedor_id:
        items_list = items_list.filter(proveedores__id=proveedor_id)
    if ubicacion_id:
        items_list = items_list.filter(ubicaciones__id=ubicacion_id)

    if disponibilidad == 'disponible':
        items_list = items_list.filter(cantidad_ingresada__gt=F('cantidad_usada'))
    elif disponibilidad == 'agotado':
        items_list = items_list.filter(cantidad_ingresada__lte=F('cantidad_usada'))
        
    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.nombre,
            'detalle': f"Quedan: {item.cantidad_restante} {item.get_unidad_medida_display()}",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]
        
        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_potreros(request):
    items_list = Potrero.objects.order_by('nombre')
    
    nombre_query = request.GET.get('nombre', '')
    empastado_query = request.GET.get('empastado')
    fumigado_query = request.GET.get('fumigado')
    rozado_query = request.GET.get('rozado')

    if nombre_query:
        items_list = items_list.filter(nombre__icontains=nombre_query)
    
    if empastado_query in ['true', 'false']:
        items_list = items_list.filter(empastado=(empastado_query == 'true'))
    if fumigado_query in ['true', 'false']:
        items_list = items_list.filter(fumigado=(fumigado_query == 'true'))
    if rozado_query in ['true', 'false']:
        items_list = items_list.filter(rozado=(rozado_query == 'true'))
        
    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.nombre,
            'detalle': f"Área: {item.area_hectareas} ha",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]
        
        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_productos_view(request):
    items_list = Producto.objects.select_related('categoria').order_by('nombre')
    
    nombre_query = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria', '')
    estado_query = request.GET.get('estado')

    if nombre_query:
        items_list = items_list.filter(nombre__icontains=nombre_query)
    if categoria_id:
        items_list = items_list.filter(categoria__id=categoria_id)
    if estado_query:
        items_list = items_list.filter(estado=estado_query)
        
    paginator = Paginator(items_list, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'id': item.id,
            'nombre': item.nombre,
            'detalle': f"Cantidad: {item.cantidad} {item.get_unidad_medida_display()}",
            'imagen_url': get_safe_image_url(item.imagen),
        } for item in page_obj.object_list]
        
        return JsonResponse({
            'items': data, 'total_pages': paginator.num_pages, 'current_page': page_obj.number
        })
    return JsonResponse({'status': 'error'}, status=400)

# AÑADE ESTE CÓDIGO AL FINAL DE TUS VISTAS

@login_required
def control_plaga_detalles_json(request, control_plaga_id):
    item = get_object_or_404(ControlPlaga, pk=control_plaga_id)

    proveedores_data = [{
        'nombre': p.nombre, 'nombre_local': p.nombre_local, 'correo': p.correo_electronico,
        'telefono': p.telefono, 'imagen_url': get_safe_image_url(p.imagen)
    } for p in item.proveedores.all()]

    ubicaciones_data = [{
        'nombre': u.nombre, 'barrio': u.barrio, 'direccion': u.direccion,
        'link': u.link, 'imagen_url': get_safe_image_url(u.imagen)
    } for u in item.ubicaciones.all()]

    data = {
        'id': item.id,
        'nombre': item.nombre_producto,
        'tipo': item.tipo,
        'cantidad_ingresada': str(item.cantidad_ingresada),
        'cantidad_usada': str(item.cantidad_usada),
        'cantidad_restante': str(item.cantidad_restante),
        'unidad_medida': item.get_unidad_medida_display(),
        'precio': str(item.precio),
        'proveedores': proveedores_data,
        'ubicaciones': ubicaciones_data,
        'fecha_compra': item.fecha_compra.strftime('%d/%m/%Y'),
        'fecha_vencimiento': item.fecha_vencimiento.strftime('%d/%m/%Y'),
        'descripcion': item.descripcion or "No hay descripción.", # AÑADE ESTA LÍNEA
        'imagen_url': get_safe_image_url(item.imagen),
    }
    return JsonResponse(data)

@require_POST
@login_required
def actualizar_cantidad_control_plaga(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('control_plaga_id')
        cantidad_a_usar = Decimal(data.get('cantidad_a_usar'))
        item = get_object_or_404(ControlPlaga, pk=item_id)

        if cantidad_a_usar <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor a cero.'}, status=400)
        if cantidad_a_usar > item.cantidad_restante:
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente cantidad en inventario.'}, status=400)
        
        item.cantidad_usada += cantidad_a_usar
        item.save()
        return JsonResponse({
            'status': 'success', 'message': 'Cantidad actualizada correctamente.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def anadir_stock_control_plaga(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('control_plaga_id')
        cantidad_a_anadir = Decimal(data.get('cantidad_a_anadir'))

        if cantidad_a_anadir <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad a añadir debe ser positiva.'}, status=400)
        
        item = get_object_or_404(ControlPlaga, pk=item_id)
        item.cantidad_ingresada += cantidad_a_anadir
        item.save()
        return JsonResponse({
            'status': 'success', 'message': 'Stock añadido correctamente.'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# AÑADE ESTE CÓDIGO AL FINAL DE TUS VISTAS
from .models import LugarMantenimiento # Asegúrate de que LugarMantenimiento esté importado

@login_required
def mantenimiento_detalles_json(request, mantenimiento_id):
    mantenimiento = get_object_or_404(Mantenimiento, pk=mantenimiento_id)
    
    lugares_data = []
    for lugar in mantenimiento.lugares_mantenimiento.all():
        lugares_data.append({
            'id': lugar.id,
            'nombre': lugar.nombre_lugar,
        })

    data = {
        'id': mantenimiento.id,
        'equipo': mantenimiento.equipo,
        'fecha_ultimo_mantenimiento': mantenimiento.fecha_ultimo_mantenimiento.strftime('%Y-%m-%d'),
        'fecha_proximo_mantenimiento': mantenimiento.fecha_proximo_mantenimiento.strftime('%Y-%m-%d'),
        'completado': mantenimiento.completado,
        'descripcion': mantenimiento.descripcion,
        'lugares_mantenimiento': lugares_data,
        'imagen_url': get_safe_image_url(mantenimiento.imagen),
    }
    return JsonResponse(data)

@login_required
def lugar_mantenimiento_detalles_json(request, lugar_id):
    lugar = get_object_or_404(LugarMantenimiento, pk=lugar_id)

    proveedores_data = [{'nombre': p.nombre} for p in lugar.proveedores.all()]
    ubicaciones_data = [{'link': u.link} for u in lugar.ubicaciones.all() if u.link]

    data = {
        'nombre_lugar': lugar.nombre_lugar,
        'nombre_empresa': lugar.nombre_empresa,
        'correo': lugar.correo,
        'numero': lugar.numero,
        'descripcion': lugar.descripcion,
        'proveedores': proveedores_data,
        'ubicaciones': ubicaciones_data,
    }
    return JsonResponse(data)


@require_POST
@login_required
def actualizar_mantenimiento(request):
    try:
        data = json.loads(request.body)
        mantenimiento_id = data.get('mantenimiento_id')
        mantenimiento = get_object_or_404(Mantenimiento, pk=mantenimiento_id)
        
        mantenimiento.fecha_ultimo_mantenimiento = data.get('fecha_ultimo', mantenimiento.fecha_ultimo_mantenimiento)
        mantenimiento.fecha_proximo_mantenimiento = data.get('fecha_proximo', mantenimiento.fecha_proximo_mantenimiento)
        mantenimiento.completado = data.get('completado', mantenimiento.completado)
        mantenimiento.save()
        
        # AÑADIDO: Registrar en el historial
        log_user_action(request, mantenimiento, CHANGE, "Mantenimiento actualizado desde el panel de usuario.")
        
        return JsonResponse({'status': 'success', 'message': 'Mantenimiento actualizado correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# AÑADE ESTE CÓDIGO AL FINAL DE TUS VISTAS
@login_required
def potrero_detalles_json(request, potrero_id):
    potrero = get_object_or_404(Potrero, pk=potrero_id)
    
    # Obtenemos todos los potreros excepto el actual para la lista de intercambio
    otros_potreros = Potrero.objects.exclude(pk=potrero_id).values('id', 'nombre')

    data = {
        'id': potrero.id,
        'nombre': potrero.nombre,
        'area_hectareas': str(potrero.area_hectareas),
        'empastado': potrero.empastado,
        'fumigado': potrero.fumigado,
        'rozado': potrero.rozado,
        'fecha_proximo_empaste': potrero.fecha_proximo_empaste.strftime('%Y-%m-%d') if potrero.fecha_proximo_empaste else '',
        'fecha_proxima_fumigacion': potrero.fecha_proxima_fumigacion.strftime('%Y-%m-%d') if potrero.fecha_proxima_fumigacion else '',
        'fecha_proximo_rozado': potrero.fecha_proximo_rozado.strftime('%Y-%m-%d') if potrero.fecha_proximo_rozado else '',
        'intercambio_con_potrero_id': potrero.intercambio_con_potrero.id if potrero.intercambio_con_potrero else None,
        'fecha_intercambio': potrero.fecha_intercambio.strftime('%Y-%m-%d') if potrero.fecha_intercambio else '',
        'descripcion': potrero.descripcion,
        'imagen_url': get_safe_image_url(potrero.imagen),
        'otros_potreros': list(otros_potreros),
    }
    return JsonResponse(data)

@require_POST
@login_required
def actualizar_potrero(request):
    try:
        data = json.loads(request.body)
        potrero_id = data.get('potrero_id')
        potrero = get_object_or_404(Potrero, pk=potrero_id)
        
        potrero.empastado = data.get('empastado', potrero.empastado)
        potrero.fumigado = data.get('fumigado', potrero.fumigado)
        potrero.rozado = data.get('rozado', potrero.rozado)
        potrero.fecha_proximo_empaste = data.get('fecha_proximo_empaste') or None
        potrero.fecha_proxima_fumigacion = data.get('fecha_proxima_fumigacion') or None
        potrero.fecha_proximo_rozado = data.get('fecha_proximo_rozado') or None
        potrero.fecha_intercambio = data.get('fecha_intercambio') or None
        
        intercambio_id = data.get('intercambio_con_potrero_id')
        if intercambio_id:
            potrero.intercambio_con_potrero = get_object_or_404(Potrero, pk=intercambio_id)
        else:
            potrero.intercambio_con_potrero = None
            
        potrero.save()
        
        # AÑADIDO: Registrar en el historial
        log_user_action(request, potrero, CHANGE, "Potrero actualizado desde el panel de usuario.")

        return JsonResponse({'status': 'success', 'message': 'Potrero actualizado correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def producto_detalles_json(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    
    # Obtener todas las fechas de producción
    fechas_produccion = list(producto.fechas_produccion.all().values_list('fecha', flat=True))
    
    # Obtener todas las ventas asociadas
    ventas = producto.ventaproducto_set.all()
    ventas_info = []
    for venta in ventas:
        ventas_info.append({
            'comprador_id': venta.comprador.id,
            'comprador_nombre': venta.comprador.nombre,
            'fecha_venta': venta.fecha_venta.strftime('%Y-%m-%d'),
            'valor_compra': str(venta.valor_compra),
            'valor_abono': str(venta.valor_abono)
        })

    ubicaciones_data = []
    for u in producto.ubicaciones.all():
        ubicaciones_data.append({
            'nombre': u.nombre,
            'barrio': u.barrio,
            'direccion': u.direccion,
            'link': u.link,
            'imagen_url': get_safe_image_url(u.imagen)
        })

    data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'categoria': {'nombre': producto.categoria.nombre} if producto.categoria else None,
        'descripcion': producto.descripcion or "No hay descripción.",
        'cantidad': str(producto.cantidad),
        'unidad_medida': producto.get_unidad_medida_display(),
        'estado': producto.estado,
        'precio': str(producto.precio),
        'precio_total': str(producto.precio_total),
        'fechas_produccion': [fecha.strftime('%Y-%m-%d') for fecha in fechas_produccion],
        'ventas': ventas_info,
        'ubicaciones': ubicaciones_data,
        'imagen_url': get_safe_image_url(producto.imagen),
        'todos_los_compradores': list(Comprador.objects.values('id', 'nombre')),
    }
    return JsonResponse(data)

@login_required
def comprador_detalles_json(request, comprador_id):
    comprador = get_object_or_404(Comprador, pk=comprador_id)
    data = {
        'nombre': comprador.nombre,
        'telefono': comprador.telefono
    }
    return JsonResponse(data)

@require_POST
@login_required
@csrf_protect
def anadir_stock_producto(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = Decimal(data.get('cantidad'))
        precio = Decimal(data.get('precio'))
        fecha_produccion = data.get('fecha_produccion')

        if not all([producto_id, cantidad, fecha_produccion, precio]):
            return JsonResponse({'status': 'error', 'message': 'Faltan datos.'}, status=400)
        
        if cantidad <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser un número positivo.'}, status=400)

        if precio <= 0:
            return JsonResponse({'status': 'error', 'message': 'El precio debe ser un número positivo.'}, status=400)

        producto = get_object_or_404(Producto, pk=producto_id)
        producto.cantidad = cantidad
        producto.precio = precio
        producto.save()

        FechaProduccion.objects.create(producto=producto, fecha=fecha_produccion)
        
        log_user_action(request, producto, CHANGE, f"Actualizó el stock a {cantidad} con fecha de producción {fecha_produccion} y precio ${precio}.")

        return JsonResponse({
            'status': 'success',
            'message': 'Stock actualizado correctamente.',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
@csrf_protect
def actualizar_producto(request):
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        producto = get_object_or_404(Producto, pk=producto_id)

        # 1. Get the new state from the request
        new_estado = data.get('estado', producto.estado)
        
        # 2. Handle sale/reservation creation
        if new_estado in ['VENDIDO', 'APARTADO']:
            comprador_id = data.get('comprador_id')
            fecha_venta = data.get('fecha_venta')

            if not comprador_id or not fecha_venta:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos del comprador o fecha de venta.'}, status=400)

            comprador = get_object_or_404(Comprador, pk=comprador_id)
            
            # Capture the state of the product at the time of sale/reservation
            latest_production_date = producto.fechas_produccion.order_by('-fecha').first()

            venta_data = {
                'producto': producto,
                'comprador': comprador,
                'fecha_venta': fecha_venta,
                'cantidad_vendida': producto.cantidad,
                'precio_unitario_venta': producto.precio,
                'fecha_produccion_venta': latest_production_date.fecha if latest_production_date else None,
            }

            if new_estado == 'VENDIDO':
                valor_compra = data.get('valor_compra')
                if not valor_compra:
                    return JsonResponse({'status': 'error', 'message': 'El valor de compra es requerido para una venta.'}, status=400)
                venta_data['valor_compra'] = Decimal(valor_compra)
                
                # Update product quantity and price to 0 on sale
                producto.cantidad = 0
                producto.precio = 0
            
            elif new_estado == 'APARTADO':
                valor_abono = data.get('valor_abono', 0.0)
                venta_data['valor_abono'] = Decimal(valor_abono)

            VentaProducto.objects.create(**venta_data)
        
        # Finally, update the product's state
        producto.estado = new_estado
        producto.save()
        
        log_user_action(request, producto, CHANGE, f"Estado del producto actualizado a {producto.get_estado_display()} desde el panel de usuario.")

        return JsonResponse({'status': 'success', 'message': 'Producto actualizado.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
@csrf_protect
def crear_comprador_ajax(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        telefono = data.get('telefono', '').strip()

        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'El nombre no puede estar vacío.'}, status=400)
        
        if Comprador.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe un comprador con este nombre.'}, status=400)

        nuevo_comprador = Comprador.objects.create(nombre=nombre, telefono=telefono)
        
        # AÑADIDO: Registrar la creación en el historial
        log_user_action(request, nuevo_comprador, ADDITION, "Comprador creado desde el panel de usuario.")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comprador creado correctamente.',
            'nuevo_comprador': { 'id': nuevo_comprador.id, 'nombre': nuevo_comprador.nombre }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def medicamento_detalles_json(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    
    proveedores_data = [{'nombre': p.nombre, 'id': p.id} for p in Proveedor.objects.all()]
    ubicaciones_data = [{'nombre': u.nombre, 'id': u.id} for u in Ubicacion.objects.all()]
    etiquetas_data = [{'nombre': e.nombre, 'id': e.id} for e in Etiqueta.objects.filter(parent__isnull=True)]

    data = {
        'id': medicamento.id,
        'nombre': medicamento.nombre,
        'cantidad_ingresada': str(medicamento.cantidad_ingresada),
        'cantidad_usada': str(medicamento.cantidad_usada),
        'cantidad_restante': str(medicamento.cantidad_restante),
        'categoria': {'nombre': medicamento.categoria.nombre} if medicamento.categoria else None,
        'precio': str(medicamento.precio),
        'proveedores': list(medicamento.proveedores.values('id', 'nombre')),
        'ubicaciones': list(medicamento.ubicaciones.values('id', 'nombre')),
        'fecha_compra': medicamento.fecha_compra.strftime('%Y-%m-%d'),
        'fecha_ingreso': medicamento.fecha_ingreso.strftime('%Y-%m-%d'),
        'fecha_vencimiento': medicamento.fecha_vencimiento.strftime('%Y-%m-%d'),
        'imagen_url': get_safe_image_url(medicamento.imagen),
        'descripcion': medicamento.descripcion or "No hay descripción.",
        'unidad_medida': medicamento.get_unidad_medida_display(),
        # Datos para el formulario de vacunas
        'all_proveedores': proveedores_data,
        'all_ubicaciones': ubicaciones_data,
        'all_etiquetas': etiquetas_data,
    }
    return JsonResponse(data)

@require_POST
@login_required
def actualizar_cantidad_medicamento(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('medicamento_id')
        cantidad = Decimal(data.get('cantidad_a_usar'))
        item = get_object_or_404(Medicamento, pk=item_id)

        if cantidad <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser positiva.'}, status=400)
        if cantidad > item.cantidad_restante:
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente stock.'}, status=400)
        
        item.cantidad_usada += cantidad
        item.save()
        log_user_action(request, item, CHANGE, f"Usó {cantidad} desde el panel de usuario.")
        return JsonResponse({'status': 'success', 'message': 'Cantidad actualizada.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def anadir_stock_medicamento(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('medicamento_id')
        cantidad = Decimal(data.get('cantidad_a_anadir'))
        item = get_object_or_404(Medicamento, pk=item_id)

        if cantidad <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser positiva.'}, status=400)
        
        item.cantidad_ingresada += cantidad
        item.save()
        log_user_action(request, item, CHANGE, f"Añadió {cantidad} al stock desde el panel de usuario.")
        return JsonResponse({'status': 'success', 'message': 'Stock añadido.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def crear_vacuna_ajax(request):
    try:
        data = json.loads(request.body)
        
        # Crear la vacuna
        nueva_vacuna = Vacuna.objects.create(
            nombre=data.get('nombre'),
            tipo=data.get('tipo'),
            disponible=data.get('disponible', True),
            cantidad=Decimal(data.get('cantidad', 0)),
            unidad_medida=data.get('unidad_medida'),
            dosis_crecimiento=data.get('dosis_crecimiento', ''),
            dosis_edad=data.get('dosis_edad', ''),
            dosis_peso=data.get('dosis_peso', ''),
            fecha_compra=data.get('fecha_compra'),
            fecha_vencimiento=data.get('fecha_vencimiento'),
            descripcion=data.get('descripcion', '')
        )

        # Añadir relaciones ManyToMany
        if data.get('proveedores'):
            nueva_vacuna.proveedores.set(data.get('proveedores'))
        if data.get('ubicaciones'):
            nueva_vacuna.ubicaciones.set(data.get('ubicaciones'))
        if data.get('etiquetas'):
            nueva_vacuna.etiquetas.set(data.get('etiquetas'))
            
        log_user_action(request, nueva_vacuna, ADDITION, "Vacuna creada desde el panel de usuario.")
        
        return JsonResponse({'status': 'success', 'message': 'Vacuna creada correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def get_vacuna_form_data(request):
    data = {
        'proveedores': list(Proveedor.objects.values('id', 'nombre')),
        'ubicaciones': list(Ubicacion.objects.values('id', 'nombre')),
        'etiquetas': list(Etiqueta.objects.filter(parent__isnull=True).values('id', 'nombre')),
    }
    return JsonResponse(data)

@login_required
def vacuna_detalles_json(request, vacuna_id):
    vacuna = get_object_or_404(Vacuna, pk=vacuna_id)
    
    data = {
        'id': vacuna.id,
        'nombre': vacuna.nombre,
        'tipo': vacuna.tipo,
        'cantidad': str(vacuna.cantidad),
        'unidad_medida': vacuna.get_unidad_medida_display(),
        'dosis_crecimiento': vacuna.dosis_crecimiento,
        'dosis_edad': vacuna.dosis_edad,
        'dosis_peso': vacuna.dosis_peso,
        'descripcion': vacuna.descripcion or "No hay descripción.",
        'disponible': vacuna.disponible,  # Devuelve booleano
        'precio': str(vacuna.precio),  # Devuelve número como cadena
        'fecha_compra': vacuna.fecha_compra.strftime('%d/%m/%Y') if vacuna.fecha_compra else '',
        'fecha_vencimiento': vacuna.fecha_vencimiento.strftime('%d/%m/%Y') if vacuna.fecha_vencimiento else '',
        'proveedores': list(vacuna.proveedores.values('id', 'nombre')),  # Devuelve lista de objetos
        'ubicaciones': list(vacuna.ubicaciones.values('id', 'nombre')),  # Devuelve lista de objetos
        'etiquetas': list(vacuna.etiquetas.values('id', 'nombre')),  # Devuelve lista de objetos
        'imagen_url': get_safe_image_url(vacuna.imagen),
    }
    return JsonResponse(data)

# AÑADE ESTE CÓDIGO AL FINAL DE TUS VISTAS

@login_required
def ganado_detalles_json(request, ganado_id):
    ganado = get_object_or_404(Ganado, pk=ganado_id)
    
    # Historial de vacunación - CÓDIGO MEJORADO
    vacunaciones = ganado.vacunaciones.select_related('vacuna').order_by('-fecha_aplicacion')
    historial_vacunacion = []
    for reg in vacunaciones:
        # Verificamos que la vacuna asociada existe antes de usarla
        if hasattr(reg, 'vacuna') and reg.vacuna:
            historial_vacunacion.append({
                'id': reg.id, 'vacuna_id': reg.vacuna.id, 'vacuna_nombre': reg.vacuna.nombre,
                'fecha_aplicacion': reg.fecha_aplicacion.strftime('%d/%m/%Y'),
                'fecha_proxima_dosis': reg.fecha_proxima_dosis.strftime('%d/%m/%Y') if reg.fecha_proxima_dosis else 'N/A',
                'notas': reg.notas or 'No hay notas.',
            })
        else: # Si no existe, lo manejamos de forma segura
            historial_vacunacion.append({
                'id': reg.id, 'vacuna_id': None, 'vacuna_nombre': f"Vacuna eliminada (ID: {reg.vacuna_id})",
                'fecha_aplicacion': reg.fecha_aplicacion.strftime('%d/%m/%Y'),
                'fecha_proxima_dosis': reg.fecha_proxima_dosis.strftime('%d/%m/%Y') if reg.fecha_proxima_dosis else 'N/A',
                'notas': 'Error: La vacuna asociada a este registro ya no existe.',
            })

    # Historial de medicamentos - CÓDIGO MEJORADO
    medicamentos_aplicados = ganado.medicamentos_aplicados.select_related('medicamento').order_by('-fecha_aplicacion')
    historial_medicamentos = []
    for reg in medicamentos_aplicados:
        # Hacemos la misma verificación para los medicamentos
        if hasattr(reg, 'medicamento') and reg.medicamento:
            historial_medicamentos.append({
                'id': reg.id, 'medicamento_id': reg.medicamento.id, 'medicamento_nombre': reg.medicamento.nombre,
                'fecha_aplicacion': reg.fecha_aplicacion.strftime('%d/%m/%Y'),
                'notas': reg.notas or 'No hay notas.',
            })
        else: # Manejo seguro si el medicamento fue eliminado
            historial_medicamentos.append({
                'id': reg.id, 'medicamento_id': None, 'medicamento_nombre': f"Medicamento eliminado (ID: {reg.medicamento_id})",
                'fecha_aplicacion': reg.fecha_aplicacion.strftime('%d/%m/%Y'),
                'notas': 'Error: El medicamento asociado a este registro ya no existe.',
            })

    estados_salud = [{'value': choice[0], 'label': choice[1]} for choice in Ganado.EstadoSalud.choices]
    tipos_preñez = [{'value': choice[0], 'label': choice[1]} for choice in Ganado.TipoPrenez.choices]
    estados_animal = [{'value': choice[0], 'label': choice[1]} for choice in Ganado.EstadoAnimal.choices]
    crecimiento_animal = [{'value': choice[0], 'label': choice[1]} for choice in Ganado.Crecimiento.choices]

    data = {
        'id': ganado.id, 'identificador': ganado.identificador,
        'animal': ganado.animal.nombre if ganado.animal else 'N/A', 'raza': ganado.raza,
        'genero': ganado.get_genero_display(), 'peso_kg': str(ganado.peso_kg),
        'edad': ganado.edad if ganado.fecha_nacimiento else 'N/A',
        'fecha_nacimiento': ganado.fecha_nacimiento.strftime('%Y-%m-%d') if ganado.fecha_nacimiento else '',
        'estado_salud': ganado.estado_salud,
        # Leemos del modelo (peñe) y lo asignamos a la clave del JSON (preñez)
        'preñez': ganado.peñe,
        'descripcion': ganado.descripcion or "No hay descripción.",
        'imagen_url': get_safe_image_url(ganado.imagen),
        'historial_vacunacion': historial_vacunacion,
        'historial_medicamentos': historial_medicamentos,
        'crecimiento': ganado.crecimiento,
        'fecha_fallecimiento': ganado.fecha_fallecimiento.strftime('%Y-%m-%d') if ganado.fecha_fallecimiento else '',
        'fecha_venta': ganado.fecha_venta.strftime('%Y-%m-%d') if ganado.fecha_venta else '',
        'valor_venta': str(ganado.valor_venta) if ganado.valor_venta is not None else '',
        'razon_venta': ganado.razon_venta or '',
        'razon_fallecimiento': ganado.razon_fallecimiento or '',
        'comprador': ganado.comprador or '',
        'comprador_telefono': ganado.comprador_telefono or '',
        # Hacemos lo mismo para los otros campos relacionados
        'fecha_preñez': ganado.fecha_peñe.strftime('%Y-%m-%d') if ganado.fecha_peñe else '',
        'descripcion_preñez': ganado.descripcion_peñe or '',
        # Datos para los formularios
        'todas_las_vacunas': list(Vacuna.objects.filter(disponible=True).values('id', 'nombre')),
        'todos_los_medicamentos': list(Medicamento.objects.filter(cantidad_ingresada__gt=F('cantidad_usada')).values('id', 'nombre')),
        'todos_los_estados_salud': estados_salud,
        'todos_los_tipos_preñez': tipos_preñez,
        'todos_los_estados': estados_animal,
        'todos_los_crecimientos': crecimiento_animal,
    }
    return JsonResponse(data)

@require_POST
@login_required
def registrar_vacunacion_ajax(request):
    try:
        data = json.loads(request.body)
        ganado_id = data.get('ganado_id')
        vacuna_id = data.get('vacuna_id')
        fecha_aplicacion = data.get('fecha_aplicacion')
        fecha_proxima_dosis = data.get('fecha_proxima_dosis') or None
        notas = data.get('notas', '')

        ganado = get_object_or_404(Ganado, pk=ganado_id)
        vacuna = get_object_or_404(Vacuna, pk=vacuna_id)

        registro = RegistroVacunacion.objects.create(
            ganado=ganado,
            vacuna=vacuna,
            fecha_aplicacion=fecha_aplicacion,
            fecha_proxima_dosis=fecha_proxima_dosis,
            notas=notas
        )
        
        log_user_action(request, registro, ADDITION, f"Registró vacunación de {vacuna.nombre} a {ganado.identificador}.")
        
        return JsonResponse({'status': 'success', 'message': 'Vacunación registrada correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def editar_registro_vacunacion(request):
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')
        registro = get_object_or_404(RegistroVacunacion, pk=registro_id)

        registro.fecha_aplicacion = data.get('fecha_aplicacion', registro.fecha_aplicacion)
        registro.fecha_proxima_dosis = data.get('fecha_proxima_dosis', registro.fecha_proxima_dosis)
        registro.notas = data.get('notas', registro.notas)
        registro.save()

        log_user_action(request, registro, CHANGE, "Registro de vacunación actualizado.")
        return JsonResponse({'status': 'success', 'message': 'Registro actualizado.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def eliminar_registro_vacunacion(request):
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')
        registro = get_object_or_404(RegistroVacunacion, pk=registro_id)
        
        # Guardar una referencia antes de eliminar para el log
        ganado_identificador = registro.ganado.identificador
        vacuna_nombre = registro.vacuna.nombre
        
        registro.delete()
        
        # No se puede usar log_user_action porque el objeto ya no existe.
        # Podrías crear un log manual si es necesario.
        
        return JsonResponse({'status': 'success', 'message': f'Se eliminó el registro de {vacuna_nombre} para {ganado_identificador}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def registrar_medicamento_ajax(request):
    try:
        data = json.loads(request.body)
        ganado_id = data.get('ganado_id')
        medicamento_id = data.get('medicamento_id')
        fecha_aplicacion = data.get('fecha_aplicacion')
        notas = data.get('notas', '')

        ganado = get_object_or_404(Ganado, pk=ganado_id)
        medicamento = get_object_or_404(Medicamento, pk=medicamento_id)

        registro = RegistroMedicamento.objects.create(
            ganado=ganado,
            medicamento=medicamento,
            fecha_aplicacion=fecha_aplicacion,
            notas=notas
        )
        
        log_user_action(request, registro, ADDITION, f"Registró aplicación de {medicamento.nombre} a {ganado.identificador}.")
        
        return JsonResponse({'status': 'success', 'message': 'Medicamento registrado correctamente.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def editar_registro_medicamento(request):
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')
        registro = get_object_or_404(RegistroMedicamento, pk=registro_id)

        registro.fecha_aplicacion = data.get('fecha_aplicacion', registro.fecha_aplicacion)
        registro.notas = data.get('notas', registro.notas)
        registro.save()

        log_user_action(request, registro, CHANGE, "Registro de medicamento actualizado.")
        return JsonResponse({'status': 'success', 'message': 'Registro actualizado.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def eliminar_registro_medicamento(request):
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')
        registro = get_object_or_404(RegistroMedicamento, pk=registro_id)
        
        ganado_identificador = registro.ganado.identificador
        medicamento_nombre = registro.medicamento.nombre
        
        registro.delete()
        
        return JsonResponse({'status': 'success', 'message': f'Se eliminó el registro de {medicamento_nombre} para {ganado_identificador}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)