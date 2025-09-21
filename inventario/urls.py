# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('redirect/', views.user_redirect, name='user_redirect'),
    path('alimento/detalles/<int:alimento_id>/', views.alimento_detalles_json, name='alimento_detalles_json'),
    path('alimento/actualizar_cantidad/', views.actualizar_cantidad_alimento, name='actualizar_cantidad_alimento'),
    path('alimento/gestionar_etiqueta/', views.gestionar_etiqueta_alimento, name='gestionar_etiqueta_alimento'),
]