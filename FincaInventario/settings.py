# FincaInventario/settings.py
"""
Django settings for FincaInventario project.
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'inventario',
    'caracteristicas',
    'historial',
]

JAZZMIN_SETTINGS = {
    "site_title": "Inventario La Matutina",
    "site_header": "La Matutina",
    "site_brand": "Panel de control",
    "site_logo": "inventario/images/logo.png",
    "custom_css": "inventario/css/logo_resize.css",
    "welcome_sign": "¡Bienvenido a la administración de La Matutina!",
    "theme": "darkly",
    "navbar_small_text": False,
    "user_avatar": None,
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["inventario"],
    "topmenu_links": [
        {"name": "Ver Vista de Usuario", "url": "lista_productos", "new_window": True},
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'FincaInventario.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'FincaInventario.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'user_redirect'
LOGOUT_REDIRECT_URL = 'login'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name="dd6ugwzzx",
    api_key="829678619421532",
    api_secret="YKO6Hw4iYwwumCoBfuRZtHGG5s0",
    secure=True
)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dd6ugwzzx',
    'API_KEY': '829678619421532',
    'API_SECRET': 'YKO6Hw4iYwwumCoBfuRZtHGG5s0',
}

# CONFIGURACIÓN DE CORREO ELECTRÓNICO
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

DEBUG = config('DEBUG', default=False, cast=bool)
IS_PRODUCTION = 'DATABASE_URL' in os.environ

# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # Directorio para collectstatic

if IS_PRODUCTION:
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    ALLOWED_HOSTS = []
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
    
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MEDIA_URL = ''

else:
    # --- Configuración para desarrollo local ---
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    # Esta es la línea clave que faltaba para decirle a Django
    # dónde encontrar los archivos estáticos de tus aplicaciones (como 'inventario')
    STATICFILES_DIRS = [
        BASE_DIR / 'inventario/static',
    ]

    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'