from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Importamos solo los modelos que SÍ existen por ahora
from .models import Producto, Ganado, Medicamento, Alimento, ControlPlaga, Potrero, Mantenimiento, Combustible


# --- Personalización del Admin de Usuarios (esto está bien, déjalo como está) ---
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

# --- Registro de Modelos en el Admin ---

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Producto)
admin.site.register(Ganado)
admin.site.register(Medicamento)
admin.site.register(Alimento)
admin.site.register(ControlPlaga)
admin.site.register(Potrero)
admin.site.register(Mantenimiento)
admin.site.register(Combustible)
# admin.site.register(Ubicacion)  <-- Comentado
# admin.site.register(MovimientoInventario) <-- Comentado