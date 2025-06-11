from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'veillesanitaire.com', 'www.veillesanitaire.com', 'https://veillesanitaire.com'
]
CSRF_TRUSTED_ORIGINS = ['https://veillesanitaire.com']
CORS_ALLOWED_ORIGINS = ['https://veillesanitaire.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}