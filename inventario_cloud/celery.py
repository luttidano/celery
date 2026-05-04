import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventario_cloud.settings')
app = Celery('inventario_cloud')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()