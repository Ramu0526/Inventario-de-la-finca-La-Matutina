# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('redirect/', views.user_redirect, name='user_redirect'),
    # --- LÍNEAS AÑADIDAS ---
    path('alimento/detalles/<int:alimento_id>/', views.alimento_detalles_json, name='alimento_detalles_json'),
    path('alimento/actualizar_cantidad/', views.actualizar_cantidad_alimento, name='actualizar_cantidad_alimento'),
]