# FincaInventario/settings.py
"""
Django settings for FincaInventario project.
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url
import cloudinary

# --- Base Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')

# --- Application Definition ---
# Make sure 'jazzmin' is the first app in this list to override Django's admin.
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd Party Apps
    'cloudinary_storage',
    'cloudinary',
    # My Apps
    'inventario',
    'caracteristicas',
    'historial',
]

# --- configuraciones del tema de jazzmin xd ---
JAZZMIN_SETTINGS = {

# --- titulogogo ---
    "site_title": "Inventario La Matutina",  # Título que aparece en la pestaña del navegador, es lit el title de html xd
    "site_header": "La Matutina",  # Título que aparece en la barra superior y en la página de login
    "site_brand": "Panel de control",
    "site_logo": "inventario/images/logo.png",  # Ruta de la imagen del logo, que debe estar en la carpeta static pndjooo, staaticccc

# --- CSS PERSONALIZAOOO ----
    "custom_css": "css/logo_resize.css",  # esta es la cosa que me fastidio fokkk

# --- login ---
    "welcome_sign": "¡Bienvenido a la administración de La Matutina!",  # Mensaje que se muestra en la página de login

# --- cositas de la pagina principal xd ---
    "theme": "darkly",  # El tema de color para la interfaz de administración
    "navbar_small_text": False,  # Si el texto de la barra de navegación es pequeño
    "user_avatar": None,  # Avatar del usuario actual
    "show_sidebar": True,  # Si la barra lateral de navegación se muestra
    "navigation_expanded": True,  # Si la barra lateral está expandida por defecto
    "hide_apps": [],  # Lista de aplicaciones que se ocultan en la barra lateral xd
    "hide_models": [],  # Lista de modelos que se ocultan en la barra lateral, like, pa que no se vean pues 
    "order_with_respect_to": ["inventario"],  # Orden en el que se muestran las aplicaciones y sus modelos :v
    
    # --- ENLACE AÑADIDO EN EL MENÚ SUPERIOR ---
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

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization & Authentication ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'user_redirect'
LOGOUT_REDIRECT_URL = 'login'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Media Files Configuration (Cloudinary) ---
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

cloudinary.config(
    cloud_name = "dd6ugwzzx",
    api_key = "829678619421532",
    api_secret = "YKO6Hw4iYwwumCoBfuRZtHGG5s0",
    secure = True
)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dd6ugwzzx',
    'API_KEY': '829678619421532',
    'API_SECRET': 'YKO6Hw4iYwwumCoBfuRZtHGG5s0',
}

IS_PRODUCTION = 'DATABASE_URL' in os.environ

if IS_PRODUCTION:
    # --- PRODUCTION SETTINGS (Render) ---
    DEBUG = False
    
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
    
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MEDIA_URL = '' # Cloudinary maneja esto

else:
    DEBUG = True
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'