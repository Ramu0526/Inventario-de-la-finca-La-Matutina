# FincaInventario/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from inventario import views as inventario_views

urlpatterns = [
    path('admin/get_sub_etiquetas/', inventario_views.get_sub_etiquetas, name='get_sub_etiquetas'),
    path('admin/', admin.site.urls),
    path('login/', inventario_views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', include('inventario.urls')),
]