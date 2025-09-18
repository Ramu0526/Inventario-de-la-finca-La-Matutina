# inventario/views.py

from django.shortcuts import render, redirect
from .models import Producto
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

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
    return render(request, 'inventario/lista_productos.html', {'productos': productos})

@login_required
def user_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin:index')
    else:
        return redirect('lista_productos')