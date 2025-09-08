# FincaInventario/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Importamos las vistas de autenticación

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de autenticación
    path('login/', auth_views.LoginView.as_view(template_name='inventario/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # URL de tu aplicación de inventario
    path('', include('inventario.urls')),
]

# --- Configuración para servir archivos multimedia en Desarrollo ---
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)