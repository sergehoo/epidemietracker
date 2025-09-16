from .base import *

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'veillesanitaire.com', 'localhost', '127.0.0.1', 'www.veillesanitaire.com', 'https://veillesanitaire.com'
]
CSRF_TRUSTED_ORIGINS = ['https://veillesanitaire.com', 'localhost:8000', '127.0.0.1:8000', ]
CORS_ALLOWED_ORIGINS = ['https://veillesanitaire.com', 'localhost:8000', '127.0.0.1:8000', ]

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
