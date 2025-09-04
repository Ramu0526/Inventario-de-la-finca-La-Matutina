# caracteristicas/apps.py
from django.apps import AppConfig

class CaracteristicasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'caracteristicas'
    verbose_name = 'Características' # <-- Añade esta línea