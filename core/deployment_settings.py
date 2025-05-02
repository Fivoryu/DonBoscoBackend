import os
import  dj_database_url
from .settings import *
from .settings import BASE_DIR
from dotenv import load_dotenv

ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'localhost')]
CSRF_TRUSTED_ORIGINS = ['https://'+os.environ.get('RENDER_EXTERNAL_HOSTNAME')]

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# load_dotenv()

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOWED_ORIGINS = [
    'https://donboscofrontend.onrender.com',
    'http://localhost:5173',  # Para desarrollo local
]
if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    CORS_ALLOWED_ORIGINS.append(f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}")

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'core.utils.custom_exception_handler',
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

STORAGES = {
  'default': {
    'BACKEND': 'django.core.files.storage.FileSystemStorage',
  },
  'staticfiles': {
    'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
  },
}

DATABASES = {
    'default': dj_database_url.config(
      default=os.environ['DATABASE_URL'],
      conn_max_age=600
    )
}

# REACT_BASE_URL = os.getenv("REAC_BASE_URL", "http://localhost:5173")


