# inventario/views.py

from django.shortcuts import render, redirect
from .models import Producto, Alimento
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json

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
    alimentos = Alimento.objects.all()  # Obtenemos todos los alimentos
    
    # Pasamos ambos a la plantilla
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
    # Busca el alimento o devuelve un error 404 si no existe
    alimento = get_object_or_404(Alimento, pk=alimento_id)

    # Prepara los datos del proveedor (si existe)
    proveedor_data = None
    if alimento.proveedor:
        proveedor_data = {
            'nombre': alimento.proveedor.nombre,
            'nombre_local': alimento.proveedor.nombre_local,
            'correo': alimento.proveedor.correo_electronico,
            'telefono': alimento.proveedor.telefono,
        }

    # Prepara los datos de la ubicación (si existe)
    ubicacion_data = None
    if alimento.ubicacion:
        ubicacion_data = {
            'nombre': alimento.ubicacion.nombre,
            'barrio': alimento.ubicacion.barrio,
            'direccion': alimento.ubicacion.direccion,
            'link': alimento.ubicacion.link,
        }

    # Construye el diccionario con todos los datos a devolver
    data = {
        'id': alimento.id,
        'nombre': alimento.nombre,
        'cantidad_ingresada': alimento.cantidad_kg_ingresada,
        'cantidad_usada': alimento.cantidad_kg_usada,
        'cantidad_restante': alimento.cantidad_kg_restante,
        'precio': alimento.precio,
        'fecha_compra': alimento.fecha_compra.strftime('%d/%m/%Y'),
        'fecha_vencimiento': alimento.fecha_vencimiento.strftime('%d/%m/%Y'),
        'imagen_url': alimento.imagen.url if alimento.imagen else '',
        'categoria': alimento.categoria.nombre if alimento.categoria else 'Sin categoría',
        'proveedor': proveedor_data,
        'ubicacion': ubicacion_data,
    }
    return JsonResponse(data)


# --- VISTA PARA ACTUALIZAR LA CANTIDAD USADA ---
@require_POST  # Solo permite peticiones POST
@login_required
def actualizar_cantidad_alimento(request):
    try:
        # Lee los datos enviados desde el JavaScript
        data = json.loads(request.body)
        alimento_id = data.get('alimento_id')
        cantidad_a_usar = float(data.get('cantidad_a_usar'))

        alimento = get_object_or_404(Alimento, pk=alimento_id)

        # Validación simple
        if cantidad_a_usar <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor a cero.'}, status=400)
        if cantidad_a_usar > alimento.cantidad_kg_restante:
            return JsonResponse({'status': 'error', 'message': 'No hay suficiente cantidad en inventario.'}, status=400)

        # Actualiza la cantidad y guarda
        alimento.cantidad_kg_usada += cantidad_a_usar
        alimento.save()

        # Devuelve una respuesta exitosa con los nuevos datos
        return JsonResponse({
            'status': 'success',
            'message': 'Cantidad actualizada correctamente.',
            'nueva_cantidad_usada': alimento.cantidad_kg_usada,
            'nueva_cantidad_restante': alimento.cantidad_kg_restante,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)