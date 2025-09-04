"""
Django settings for FincaInventario project.
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# La SECRET_KEY se leerá de una variable de entorno en Render.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-bscvq*r(6i$j13m-=lr7&wdnro=oc0*z0*yjf^@-&4m2)44+d!')

# Render pone una variable 'RENDER' automáticamente. La usamos para diferenciar producción de desarrollo.
IS_RENDER = 'RENDER' in os.environ

# SECURITY WARNING: don't run with debug turned on in production!
if IS_RENDER:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = []

# Render también nos da el nombre del host automáticamente.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# También permite el acceso local para desarrollo.
ALLOWED_HOSTS.append('localhost')
ALLOWED_HOSTS.append('127.0.0.1')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventario',
    'caracteristicas',
    'historial',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Middleware de WhiteNoise
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
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

if IS_RENDER:
    # Usa la base de datos de Render (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Usa la base de datos local (SQLite) para desarrollo
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# ... (el resto de esta sección es igual) ...

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# ... (el resto de esta sección es igual) ...

LANGUAGE_CODE = 'es-co' # Cambiado a español de Colombia
TIME_ZONE = 'America/Bogota' # Cambiado a la zona horaria de Colombia
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Le decimos a Django cuál es nuestra URL de login personalizada
LOGIN_URL = 'login'

# A dónde ir después de un login exitoso
LOGIN_REDIRECT_URL = '/'

# Esta configuración es para que WhiteNoise funcione en Render
if IS_RENDER:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# ... (el resto de esta sección es igual) ...

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
