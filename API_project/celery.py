import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "API_project.settings")
app = Celery("API_project")
app.config_from_object('API_project.celeryconfig')
app.autodiscover_tasks()
