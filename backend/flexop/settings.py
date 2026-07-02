"""
Django settings for flexop project - FLEX-OP Platform
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
if not DEBUG:
    _secret_key = os.getenv('SECRET_KEY')
    if not _secret_key:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'SECRET_KEY must be set in the environment when DEBUG=False.'
        )
    SECRET_KEY = _secret_key
else:
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'django-insecure-dev-key-change-in-production-12345',
    )

def _parse_hosts(value: str) -> list[str]:
    return [host.strip() for host in value.split(',') if host.strip()]


_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()

if DEBUG:
    ALLOWED_HOSTS = _parse_hosts(os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1'))
    if _render_host:
        ALLOWED_HOSTS.append(_render_host)
else:
    _allowed_hosts = os.getenv('ALLOWED_HOSTS', '').strip()
    hosts = _parse_hosts(_allowed_hosts) if _allowed_hosts and _allowed_hosts != '*' else []
    if _render_host and _render_host not in hosts:
        hosts.append(_render_host)
    if not hosts:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'ALLOWED_HOSTS must be set explicitly when DEBUG=False (no wildcard). '
            'On Render, set ALLOWED_HOSTS=flexop-api.onrender.com or rely on '
            'RENDER_EXTERNAL_HOSTNAME.'
        )
    ALLOWED_HOSTS = hosts


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    
    # Local apps - Modulos de FLEX-OP
    'usuarios',        # Gestion de usuarios, empresas y autenticacion
    'maquinas',        # Gestion de maquinas y productos
    'operaciones',     # Turnos, operarios, asignaciones e incidencias
    'metricas',        # Registros de produccion y metricas de eficiencia
    'alertas',         # Sistema de alertas y notificaciones
    'reasignaciones',  # Sugerencias inteligentes de reasignacion
    'reportes',        # Dashboards y exportacion de reportes
    'ordenes',         # Ordenes de produccion y cola de despacho
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS debe ir temprano
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'flexop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'flexop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

_database_url = os.getenv('DATABASE_URL')
if _database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'America/Lima'  # Ajustar según ubicación

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SERVE_MEDIA = os.getenv('SERVE_MEDIA', 'False') == 'True'

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'usuarios.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'login': '10/minute',
    },
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 1440))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
# En DEBUG se permite todo; en producción se usa la variable de entorno
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            'CORS_ALLOWED_ORIGINS',
            'http://localhost:3000,http://127.0.0.1:3000',
        ).split(',')
        if origin.strip()
    ]

CORS_ALLOW_CREDENTIALS = True

# Swagger/OpenAPI Configuration
SWAGGER_USE_COMPAT_RENDERERS = False

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

