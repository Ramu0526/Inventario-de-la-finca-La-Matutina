import os
import django
from django.contrib.auth import get_user_model

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FincaInventario.settings')
django.setup()

User = get_user_model()

# Lee las variables de entorno
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Verifica que las variables existan
if not all([username, email, password]):
    print("Faltan las variables de entorno para crear el superusuario. Omitiendo.")
else:
    # Verifica si el superusuario ya existe
    if not User.objects.filter(username=username).exists():
        print(f"Creando superusuario: {username}")
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
    else:
        print(f"El superusuario '{username}' ya existe. Omitiendo.")