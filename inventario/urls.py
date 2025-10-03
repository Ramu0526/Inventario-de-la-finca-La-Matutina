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

    # AÑADE ESTAS LÍNEAS PARA CONTROL DE PLAGAS
    path('control-plaga/detalles/<int:control_plaga_id>/', views.control_plaga_detalles_json, name='control_plaga_detalles_json'),
    path('control-plaga/actualizar_cantidad/', views.actualizar_cantidad_control_plaga, name='actualizar_cantidad_control_plaga'),
    path('control-plaga/anadir_stock/', views.anadir_stock_control_plaga, name='anadir_stock_control_plaga'),

    # AÑADE ESTAS LÍNEAS PARA MANTENIMIENTO
    path('mantenimiento/detalles/<int:mantenimiento_id>/', views.mantenimiento_detalles_json, name='mantenimiento_detalles_json'),
    path('lugar-mantenimiento/detalles/<int:lugar_id>/', views.lugar_mantenimiento_detalles_json, name='lugar_mantenimiento_detalles_json'),
    path('mantenimiento/actualizar/', views.actualizar_mantenimiento, name='actualizar_mantenimiento'),

    # AÑADE ESTAS LÍNEAS PARA POTREROS
    path('potrero/detalles/<int:potrero_id>/', views.potrero_detalles_json, name='potrero_detalles_json'),
    path('potrero/actualizar/', views.actualizar_potrero, name='actualizar_potrero'),

    # AÑADE ESTAS LÍNEAS PARA PRODUCTOS
    path('producto/detalles/<int:producto_id>/', views.producto_detalles_json, name='producto_detalles_json'),
    path('producto/actualizar/', views.actualizar_producto, name='actualizar_producto'),
    path('producto/anadir_stock/', views.anadir_stock_producto, name='anadir_stock_producto'),
    path('comprador/detalles/<int:comprador_id>/', views.comprador_detalles_json, name='comprador_detalles_json'),
    path('comprador/crear/', views.crear_comprador_ajax, name='crear_comprador_ajax'),

    # AÑADE ESTAS LÍNEAS PARA MEDICAMENTOS Y VACUNAS
    path('medicamento/detalles/<int:medicamento_id>/', views.medicamento_detalles_json, name='medicamento_detalles_json'),
    path('medicamento/actualizar_cantidad/', views.actualizar_cantidad_medicamento, name='actualizar_cantidad_medicamento'),
    path('medicamento/anadir_stock/', views.anadir_stock_medicamento, name='anadir_stock_medicamento'),
    path('vacuna/crear/', views.crear_vacuna_ajax, name='crear_vacuna_ajax'),
    path('vacuna/detalles/<int:vacuna_id>/', views.vacuna_detalles_json, name='vacuna_detalles_json'),

    # AÑADE ESTAS LÍNEAS PARA GANADO
    path('ganado/detalles/<int:ganado_id>/', views.ganado_detalles_json, name='ganado_detalles_json'),
    path('ganado/registrar_vacunacion/', views.registrar_vacunacion_ajax, name='registrar_vacunacion_ajax'),
    path('ganado/editar_vacunacion/', views.editar_registro_vacunacion, name='editar_registro_vacunacion'),
    path('ganado/eliminar_vacunacion/', views.eliminar_registro_vacunacion, name='eliminar_registro_vacunacion'),
    path('ganado/registrar_medicamento/', views.registrar_medicamento_ajax, name='registrar_medicamento_ajax'),
    path('ganado/editar_medicamento/', views.editar_registro_medicamento, name='editar_registro_medicamento'),
    path('ganado/eliminar_medicamento/', views.eliminar_registro_medicamento, name='eliminar_registro_medicamento'),
    path('ganado/actualizar/', views.actualizar_ganado_ajax, name='actualizar_ganado_ajax'),
    path('get_vacuna_form_data/', views.get_vacuna_form_data, name='get_vacuna_form_data'),
    

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