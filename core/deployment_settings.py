# core/deployment_settings.py

import os
from .settings import *          # Importa TODO lo de settings.py :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
import dj_database_url          # Necesitas pip install dj-database-url

# 1. SECRET_KEY y DEBUG por entorno
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# 2. Hosts permitidos
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')  
# Ejemplo: ALLOWED_HOSTS=tu-app.onrender.com,localhost

# 3. Base de datos desde DATABASE_URL
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# 4. WhiteNoise para estáticos
MIDDLEWARE.insert(
    MIDDLEWARE.index('django.middleware.security.SecurityMiddleware') + 1,
    'whitenoise.middleware.WhiteNoiseMiddleware'
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 5. CORS: añade tu dominio de frontend en Render
CORS_ALLOWED_ORIGINS = [
    os.environ.get('FRONTEND_URL', 'http://localhost:5173'),
]
