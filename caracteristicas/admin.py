from django.contrib import admin
# Importamos los modelos de ESTA app ('caracteristicas')
from .models import Categoria, Proveedor, Ubicacion, Etiqueta

# Registramos los modelos de 'caracteristicas'
admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Ubicacion)
admin.site.register(Etiqueta)