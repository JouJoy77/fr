import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fr.settings')

app = Celery('fr')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()