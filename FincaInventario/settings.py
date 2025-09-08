"""
Django settings for FincaInventario project.
"""

from pathlib import Path
# Se eliminan las importaciones de dj_database_url y decouple

BASE_DIR = Path(__file__).resolve().parent.parent

# Se elimina la lógica de decouple para SECRET_KEY y CLOUDINARY_URL
# La SECRET_KEY se vuelve a poner directamente (puedes cambiarla después)
SECRET_KEY = 'django-insecure-a5b&z!m8(0y@q*v2-c9+j$l#p!k_f@x)o=h-n&3b*g'

# DEBUG se establece en True para desarrollo local
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Se eliminan 'cloudinary_storage' y 'cloudinary'
    
    # Mis aplicaciones
    'inventario',
    'caracteristicas',
    'historial',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Whitenoise puede quedarse, es útil
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

# Database
# Se revierte a la configuración simple de SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization & Authentication
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Se eliminan MEDIA_URL, MEDIA_ROOT, DEFAULT_FILE_STORAGE y la lógica de Render para STATIC_ROOT
# Si tenías una carpeta de staticfiles en la raíz, puedes añadir esta línea:
# STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'