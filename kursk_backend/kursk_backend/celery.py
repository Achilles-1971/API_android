import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kursk_backend.settings')

app = Celery('kursk_backend')

# Настройки Celery (включая CELERY_BROKER_URL) берутся из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'