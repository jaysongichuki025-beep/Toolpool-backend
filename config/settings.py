"""
═══════════════════════════════════════════════════════════════════════════
config/settings.py — Central configuration for the entire Django project
═══════════════════════════════════════════════════════════════════════════
WHY this file exists:
  Every Django setting (database, auth, CORS, JWT, installed apps) lives here.
  Django reads this once when the server starts.
═══════════════════════════════════════════════════════════════════════════
"""

# ── IMPORTS ───────────────────────────────────────────────────────────────
# Path helps build file paths that work on Windows, Mac, and Linux
from pathlib import Path

# os.environ.get() reads environment variables (from Docker or .env)
import os

# load_dotenv() reads a local .env file into os.environ (for local development)
from dotenv import load_dotenv

# ── LOAD .env FILE (if it exists) ─────────────────────────────────────────
# WHY: keeps secrets out of source code. Docker also injects env vars directly.
load_dotenv()

# BASE_DIR = the project-backend/ folder (one level up from config/)
BASE_DIR = Path(__file__).resolve().parent.parent

# ── SECURITY ──────────────────────────────────────────────────────────────
# SECRET_KEY signs cookies and tokens. Change it in production!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-change-me-before-deploying'
)

# DEBUG=True shows detailed error pages. NEVER True in production.
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS = domains/IPs allowed to hit this server
# Split comma-separated string from env into a Python list
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

# ── INSTALLED APPS ────────────────────────────────────────────────────────
# WHY: Django only loads code from apps listed here.
INSTALLED_APPS = [
    # Built-in Django apps
    'django.contrib.admin',       # /admin/ panel
    'django.contrib.auth',        # User authentication system
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party packages
    'rest_framework',             # Django REST Framework (JSON APIs)
    'rest_framework_simplejwt',   # JWT token auth
    'corsheaders',                # Cross-Origin Resource Sharing for React
    'django_filters',             # Filtering querysets via URL params

    # Our apps (inside the apps/ package)
    # Use full AppConfig path so users.signals.ready() runs on startup
    'apps.users.apps.UsersConfig',
    'apps.tools.apps.ToolsConfig',
    'apps.rentals.apps.RentalsConfig',
]

# ── MIDDLEWARE ────────────────────────────────────────────────────────────
# WHY: Middleware runs on EVERY request/response (security, CORS, sessions).
# Order matters — CorsMiddleware must be high (near the top).
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files in prod
    'corsheaders.middleware.CorsMiddleware',       # handle CORS before CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── URL / TEMPLATES / WSGI ────────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'  # root URL router file

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
# WHY: Use PostgreSQL when DATABASE_URL is set (Docker/production).
# Fall back to SQLite for quick local testing without Docker.
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL.startswith('postgres'):
    # Parse postgres://USER:PASSWORD@HOST:PORT/DBNAME
    # Example: postgres://toolpool:toolpool@db:5432/toolpool
    # urllib.parse is a built-in Python module for URL parsing
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
    # SQLite = single file database. Great for beginners / quick tests.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── CUSTOM USER MODEL ─────────────────────────────────────────────────────
# WHY: We use email instead of username for login.
# MUST be set before the first migration.
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
# Static = CSS/JS for Django admin. Media = user-uploaded tool photos.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # collectstatic destination
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type for new models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── DJANGO REST FRAMEWORK ─────────────────────────────────────────────────
# WHY: These defaults apply to ALL API views unless overridden.
REST_FRAMEWORK = {
    # Use JWT by default (Bearer token in Authorization header)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Require login unless a view sets permission_classes = [AllowAny]
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Enable ?search= and django-filter backends on list views
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    # Paginate list results so we never return thousands of rows at once
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

# ── SIMPLE JWT SETTINGS ───────────────────────────────────────────────────
# WHY: Access tokens are short-lived (safer). Refresh tokens renew them.
from datetime import timedelta  # noqa: E402  (imported here near JWT config for clarity)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),   # expires after 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),       # refresh valid for 1 week
    'ROTATE_REFRESH_TOKENS': False,                   # keep same refresh token
    'AUTH_HEADER_TYPES': ('Bearer',),                 # "Authorization: Bearer <token>"
}

# ── CORS (Cross-Origin Resource Sharing) ──────────────────────────────────
# WHY: Browser blocks React (localhost:5173) from calling API (localhost:8000)
# unless we explicitly allow it.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173'
    ).split(',')
    if origin.strip()
]

# Allow cookies/credentials if we ever switch to cookie-based auth later
CORS_ALLOW_CREDENTIALS = True
