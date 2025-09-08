"""
Django settings for FincaInventario project.
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Lee las variables desde el archivo .env o las variables de entorno de Render
SECRET_KEY = config('SECRET_KEY')

# DEBUG es True solo si la variable de entorno DEBUG es 'True'.
# En Render, como no existirá, será False por defecto.
DEBUG = config('DEBUG', default=False, cast=bool)

# Configuración de hosts permitidos
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
RENDER_EXTERNAL_HOSTNAME = config('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de terceros
    'cloudinary_storage',
    'cloudinary',
    
    # Mis aplicaciones
    'inventario',
    'caracteristicas',
    'historial',
]

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

# Database
# Usa la base de datos de Render si la variable DATABASE_URL existe en el entorno
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else: # Si no, usa SQLite para desarrollo local
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
MEDIA_URL = '/media/'

# En desarrollo, los medios se guardan localmente
if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# En producción, se configuran para Cloudinary
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    # Configuración de Cloudinary
    CLOUDINARY_URL = config('CLOUDINARY_URL', default=None)
    if CLOUDINARY_URL:
        DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
        CLOUDINARY_STORAGE = {
            'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
            'API_KEY': config('CLOUDINARY_API_KEY'),
            'API_SECRET': config('CLOUDINARY_API_SECRET'),
        }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'