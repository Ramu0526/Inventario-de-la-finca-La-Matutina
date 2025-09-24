# inventario/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Alimento
from caracteristicas.models import Etiqueta, Categoria, Proveedor
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from decimal import Decimal
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator

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
    # This view now handles both initial load and AJAX requests for filtering/pagination
    alimentos_list = Alimento.objects.select_related('categoria').prefetch_related('proveedores', 'ubicaciones').order_by('nombre')

    # Get filter parameters
    nombre_query = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor', '')

    if nombre_query:
        alimentos_list = alimentos_list.filter(nombre__icontains=nombre_query)
    if categoria_id:
        alimentos_list = alimentos_list.filter(categoria__id=categoria_id)
    if proveedor_id:
        alimentos_list = alimentos_list.filter(proveedores__id=proveedor_id)

    # The JS will send the items per page based on screen size
    try:
        items_per_page = int(request.GET.get('items_per_page', 8))
    except (ValueError, TypeError):
        items_per_page = 8

    paginator = Paginator(alimentos_list, items_per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # For AJAX requests, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        alimentos_data = []
        for alimento in page_obj.object_list:
            alimentos_data.append({
                'id': alimento.id,
                'nombre': alimento.nombre,
                'cantidad_kg_ingresada': alimento.cantidad_kg_ingresada,
                'imagen_url': alimento.imagen.url if alimento.imagen else None,
            })
        
        return JsonResponse({
            'alimentos': alimentos_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    # For initial page load, render the template but let JS fetch the aliments
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.all()
    
    context = {
        'alimentos': [], # Pass an empty list, JS will fetch the first page
        'categorias': categorias,
        'proveedores': proveedores,
        'productos': Producto.objects.all(), # Keep for compatibility if used elsewhere
    }
    return render(request, 'inventario/lista_productos.html', context)

@login_required
def user_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin:index')
    else:
        return redirect('lista_productos')

@login_required
def alimento_detalles_json(request, alimento_id):
    alimento = get_object_or_404(Alimento, pk=alimento_id)

    etiquetas_del_alimento = list(alimento.etiquetas.values('id', 'nombre', 'parent_id'))
    todas_las_etiquetas_principales = list(Etiqueta.objects.filter(parent__isnull=True).values('id', 'nombre'))
    
    proveedores_data = []
    for proveedor in alimento.proveedores.all():
        proveedores_data.append({
            'nombre': proveedor.nombre,
            'nombre_local': getattr(proveedor, 'nombre_local', ''),
            'correo': getattr(proveedor, 'correo_electronico', ''),
            'telefono': getattr(proveedor, 'telefono', ''),
            'imagen_url': proveedor.imagen.url if hasattr(proveedor, 'imagen') and proveedor.imagen else ''
        })

    ubicaciones_data = []
    for ubicacion in alimento.ubicaciones.all():
        ubicaciones_data.append({
            'nombre': ubicacion.nombre, 'barrio': ubicacion.barrio,
            'direccion': ubicacion.direccion, 'link': ubicacion.link,
            'imagen_url': ubicacion.imagen.url if ubicacion.imagen else ''
        })
    
    estado = "Disponible" if alimento.cantidad_kg_restante > 0 else "Agotado"

    data = {
        'id': alimento.id,
        'nombre': alimento.nombre,
        'cantidad_ingresada': alimento.cantidad_kg_ingresada,
        'cantidad_usada': alimento.cantidad_kg_usada,
        'cantidad_restante': alimento.cantidad_kg_restante,
        'precio': alimento.precio,
        'estado': estado,
        'fecha_compra': alimento.fecha_compra.strftime('%d/%m/%Y'),
        'fecha_vencimiento': alimento.fecha_vencimiento.strftime('%d/%m/%Y'),
        'imagen_url': alimento.imagen.url if alimento.imagen else '',
        'categoria': { 'id': alimento.categoria.id, 'nombre': alimento.categoria.nombre } if alimento.categoria else None,
        'proveedores': proveedores_data,
        'ubicaciones': ubicaciones_data,
        'etiquetas': etiquetas_del_alimento,
        'todas_las_etiquetas_principales': todas_las_etiquetas_principales,
    }
    return JsonResponse(data)

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
        return JsonResponse({
            'status': 'success', 'message': 'Cantidad actualizada correctamente.',
            'nueva_cantidad_usada': alimento.cantidad_kg_usada,
            'nueva_cantidad_restante': alimento.cantidad_kg_restante,
        })
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

        return JsonResponse({
            'status': 'success',
            'message': 'Stock añadido correctamente.',
            'nueva_cantidad_ingresada': alimento.cantidad_kg_ingresada,
            'nueva_cantidad_restante': alimento.cantidad_kg_restante,
        })
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Datos inválidos.'}, status=400)
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