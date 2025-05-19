# core/deployment_settings.py

import os
import sys
from pathlib import Path
from .settings import *  # hereda configuración base

# 1. Añadir carpeta de aplicaciones al PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configuración de entorno
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# 3. Base de datos desde DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# 4. WhiteNoise para servir estáticos
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
    'whitenoise.middleware.WhiteNoiseMiddleware'
)
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 5. CORS: solo origen de frontend
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'http://localhost:5173', 'http://192.168.0.11:5173'),
]

CSRF_TRUSTED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'http://localhost:5173', 'http://192.168.0.11:5173'),
]
