# inventario/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Alimento
from caracteristicas.models import Etiqueta, Categoria
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from decimal import Decimal

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
    productos = Producto.objects.all()
    alimentos = Alimento.objects.all()
    context = {
        'productos': productos,
        'alimentos': alimentos,
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
    etiquetas_del_alimento = list(alimento.etiquetas.values('id', 'nombre'))
    todas_las_etiquetas = list(Etiqueta.objects.values('id', 'nombre'))
    proveedor_data = None
    proveedor = alimento.proveedores.first()
    if proveedor:
        proveedor_data = {
            'nombre': proveedor.nombre,
            'nombre_local': getattr(proveedor, 'nombre_local', ''),
            'correo': getattr(proveedor, 'correo_electronico', ''),
            'telefono': getattr(proveedor, 'telefono', ''),
            'imagen_url': proveedor.imagen.url if hasattr(proveedor, 'imagen') and proveedor.imagen else ''
        }
    ubicacion_data = None
    if alimento.ubicacion:
        ubicacion_data = {
            'nombre': alimento.ubicacion.nombre, 'barrio': alimento.ubicacion.barrio,
            'direccion': alimento.ubicacion.direccion, 'link': alimento.ubicacion.link,
            'imagen_url': alimento.ubicacion.imagen.url if alimento.ubicacion.imagen else ''
        }
    data = {
        'id': alimento.id, 'nombre': alimento.nombre,
        'cantidad_ingresada': alimento.cantidad_kg_ingresada, 'cantidad_usada': alimento.cantidad_kg_usada,
        'cantidad_restante': alimento.cantidad_kg_restante, 'precio': alimento.precio,
        'fecha_compra': alimento.fecha_compra.strftime('%d/%m/%Y'), 'fecha_vencimiento': alimento.fecha_vencimiento.strftime('%d/%m/%Y'),
        'imagen_url': alimento.imagen.url if alimento.imagen else '',
        'categoria': alimento.categoria.nombre if alimento.categoria else 'Sin categoría',
        'proveedor': proveedor_data, 'ubicacion': ubicacion_data,
        'etiquetas': etiquetas_del_alimento, 'todas_las_etiquetas': todas_las_etiquetas,
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