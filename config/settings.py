"""
═══════════════════════════════════════════════════════════════════════════
config/settings.py — Central configuration for the entire Django project
═══════════════════════════════════════════════════════════════════════════
"""

# ── IMPORTS ───────────────────────────────────────────────────────────────
from pathlib import Path
import os
from dotenv import load_dotenv

# ── LOAD .env FILE (if it exists) ─────────────────────────────────────────
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-change-me-before-deploying'
)

DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# ── INSTALLED APPS ────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Built-in Django apps
    'django.contrib.admin',       # /admin/ panel
    'django.contrib.auth',        # User authentication system
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    
    # Cloudinary storage (must come BEFORE staticfiles)
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',                 # Core Cloudinary SDK

    # Third-party packages
    'rest_framework',             # Django REST Framework
    'rest_framework_simplejwt',   # JWT token auth
    'corsheaders',                # CORS middleware support
    'django_filters',             # Filtering querysets

    # Local apps
    'apps.users.apps.UsersConfig',
    'apps.tools.apps.ToolsConfig',
    'apps.rentals.apps.RentalsConfig',
]

# ── MIDDLEWARE ────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static assets in prod
    'corsheaders.middleware.CorsMiddleware',       # CORS handling
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── URL / TEMPLATES / WSGI ────────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# ── DATABASE ──────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL.startswith('postgres'):
    from urllib.parse import urlparse

    db_url = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_url.path[1:],          # strip leading "/"
            'USER': db_url.username,
            'PASSWORD': db_url.password,
            'HOST': db_url.hostname,
            'PORT': db_url.port or 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── CUSTOM USER MODEL ─────────────────────────────────────────────────────
AUTH_USER_MODEL = 'users.User'

# ── PASSWORD VALIDATION ───────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── INTERNATIONALIZATION ──────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ── STATIC & MEDIA FILES ──────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Standard WhiteNoise storage to avoid post-processing failures
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# Cloudinary Configuration
CLOUDINARY_CLOUD = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

if CLOUDINARY_CLOUD and CLOUDINARY_KEY and CLOUDINARY_SECRET:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD,
        'API_KEY': CLOUDINARY_KEY,
        'API_SECRET': CLOUDINARY_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── DJANGO REST FRAMEWORK ─────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# ── SIMPLE JWT SETTINGS ───────────────────────────────────────────────────
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ── CORS ──────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True