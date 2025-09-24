# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('redirect/', views.user_redirect, name='user_redirect'),
    
    # URLs de Alimentos
    path('alimento/detalles/<int:alimento_id>/', views.alimento_detalles_json, name='alimento_detalles_json'),
    path('alimento/actualizar_cantidad/', views.actualizar_cantidad_alimento, name='actualizar_cantidad_alimento'),
    path('alimento/gestionar_etiqueta/', views.gestionar_etiqueta_alimento, name='gestionar_etiqueta_alimento'),    path('alimento/anadir_stock/', views.anadir_stock_alimento, name='anadir_stock_alimento'),
    path('alimento/crear_etiqueta/', views.crear_etiqueta_ajax, name='crear_etiqueta_ajax'),
    path('alimento/crear_categoria/', views.crear_categoria_ajax, name='crear_categoria_ajax'),
    path('alimento/asignar_categoria/', views.asignar_categoria_ajax, name='asignar_categoria_ajax'),
    
    # URLs de Combustibles
    path('combustible/detalles/<int:combustible_id>/', views.combustible_detalles_json, name='combustible_detalles_json'),
    path('combustible/actualizar_cantidad/', views.actualizar_cantidad_combustible, name='actualizar_cantidad_combustible'),
    path('combustible/anadir_stock/', views.anadir_stock_combustible, name='anadir_stock_combustible'),

    # URLs para las listas de los modales
    path('alimentos/', views.lista_alimentos, name='lista_alimentos'),
    path('combustibles/', views.lista_combustibles, name='lista_combustibles'),
    path('control-plagas/', views.lista_control_plagas, name='lista_control_plagas'),
    path('ganado/', views.lista_ganado, name='lista_ganado'),
    path('mantenimientos/', views.lista_mantenimientos, name='lista_mantenimientos'),
    path('medicamentos/', views.lista_medicamentos, name='lista_medicamentos'),
    path('potreros/', views.lista_potreros, name='lista_potreros'),
    path('productos/', views.lista_productos_view, name='lista_productos_view'),
]