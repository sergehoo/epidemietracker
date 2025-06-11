from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']
CORS_ALLOWED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'epidemitracker',
        'USER': 'postgres',
        'PASSWORD': 'weddingLIFE18',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}

# gdal-config --libs >---commande linux ou mac os

GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH', '/opt/homebrew/opt/gdal/lib/libgdal.dylib')
GEOS_LIBRARY_PATH = os.getenv('GEOS_LIBRARY_PATH', '/opt/homebrew/opt/geos/lib/libgeos_c.dylib')