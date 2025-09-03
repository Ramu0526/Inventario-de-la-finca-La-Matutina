# inventario/views.py

from django.shortcuts import render
from .models import Producto
from django.contrib.auth.decorators import login_required # Importamos el decorador

@login_required # ¡Esta es la magia!
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/lista_productos.html', {'productos': productos})