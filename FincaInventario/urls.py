# FincaInventario/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventario import views as inventario_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de autenticación
    path('login/', inventario_views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # URL de tu aplicación de inventario
    path('', include('inventario.urls')),
]