# gestion_bar/settings.py

from pathlib import Path
import os  # Asegúrate de que esta importación esté
import dj_database_url # y esta también

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN DE SECRET_KEY ---
# Lee la SECRET_KEY de las variables de entorno de Render.
# El segundo valor es uno por defecto que SÓLO se usará en tu PC.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-tu-llave-secreta-local')

# --- CONFIGURACIÓN DE DEBUG ---
# DEBUG será True solo si la variable de entorno DEBUG se establece en 'True'
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# --- CONFIGURACIÓN DE ALLOWED_HOSTS ---
ALLOWED_HOSTS = []

# Render añadirá automáticamente su propio nombre de host aquí.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# También permite el acceso local para pruebas
ALLOWED_HOSTS.append('127.0.0.1')
ALLOWED_HOSTS.append('localhost')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'productos',
    'ventas',
    'reportes',
    'juegos'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise debe ir aquí, justo después de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestion_bar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_bar.wsgi.application'


# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Usará la base de datos de Render si está disponible, si no, la local.
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# Password validation
# ... (esta sección no se cambia) ...


# Internationalization
# ... (esta sección no se cambia, asegúrate de que LANGUAGE_CODE sea 'es-CO') ...
LANGUAGE_CODE = 'es-CO'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS ---
STATIC_URL = 'static/'
# Directorio donde 'collectstatic' copiará los archivos para producción.
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Habilitamos el almacenamiento de WhiteNoise.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIÓN DE LOGIN/LOGOUT ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'panel_mesas'
LOGOUT_REDIRECT_URL = 'login'