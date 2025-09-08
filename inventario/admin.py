from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.html import format_html
from django.urls import reverse

# Importamos SOLAMENTE los modelos que viven en la app 'inventario'
from .models import (Producto, Ganado, Medicamento, Alimento, 
                     ControlPlaga, Potrero, Mantenimiento, Combustible)

# --- 1. Clases de Personalización del Admin ---

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Nombre"
        self.fields['last_name'].label = "Apellido"

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    fieldsets = (
        (None, {"fields": ("username", "password_change_link",)}),
        ("Información personal", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permisos",
            { "fields": ("is_active", "is_staff", "is_superuser") }
        ),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ('password_change_link',)

    def password_change_link(self, obj):
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return format_html('<a href="{}">Restablecer contraseña</a>', url)
    password_change_link.short_description = "Contraseña"

# --- SECCIÓN CORREGIDA ---
class ProductoAdmin(admin.ModelAdmin):
    # Eliminamos 'imagen_thumbnail' porque el campo 'imagen' ya no existe
    list_display = ('nombre', 'cantidad', 'categoria')
    # Ya no necesitamos la función imagen_thumbnail, así que la eliminamos

# --- 2. Registro de Modelos en el Admin (Forma Correcta) ---

# Ocultamos el modelo Group del admin
admin.site.unregister(Group)

# Registramos User con su personalización
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registramos Producto con su personalización
admin.site.register(Producto, ProductoAdmin)

# Registramos el resto de los modelos de 'inventario' (usarán el admin por defecto)
admin.site.register(Ganado)
admin.site.register(Medicamento)
admin.site.register(Alimento)
admin.site.register(ControlPlaga)
admin.site.register(Potrero)
admin.site.register(Mantenimiento)
admin.site.register(Combustible)