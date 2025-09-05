from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.html import format_html
from django.urls import reverse

# Importamos SOLAMENTE los modelos que viven en la app 'inventario'
from .models import (Producto, Ganado, Medicamento, Alimento, 
                     ControlPlaga, Potrero, Mantenimiento, Combustible)

class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Nombre"
        self.fields['last_name'].label = "Apellido"

# --- Personalización del Admin de Usuarios (CON EL ENLACE CORREGIDO) ---
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

    # MÉTODO CORREGIDO
    def password_change_link(self, obj):
        # Usamos 'reverse' para obtener la URL correcta y segura para cambiar la contraseña
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return format_html('<a href="{}">Restablecer contraseña</a>', url)
    password_change_link.short_description = "Contraseña"
# --- Registro de Modelos en el Admin ---

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Registramos SOLAMENTE los modelos de la app 'inventario'
admin.site.register(Producto)
admin.site.register(Ganado)
admin.site.register(Medicamento)
admin.site.register(Alimento)
admin.site.register(ControlPlaga)
admin.site.register(Potrero)
admin.site.register(Mantenimiento)
admin.site.register(Combustible)