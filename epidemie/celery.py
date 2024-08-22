from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epidemietrackr.settings')

app = Celery('epidemietrackr')

# Charger les paramètres à partir du fichier de configuration de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Charger automatiquement les modules `tasks.py` des applications Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
