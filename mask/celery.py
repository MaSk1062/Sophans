import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mask.settings')
from celery.schedules import crontab


app = Celery('mask')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # Executes every Monday morning at 8:30 a.m.
    'Due date reminder': {
        'task': 'stephan.tasks.reminder_email_task',
        'schedule': crontab(hour=8, minute=30),
    },
}