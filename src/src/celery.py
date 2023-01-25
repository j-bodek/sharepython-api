import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
app = Celery("src")
# define config file (in our case django settings)
app.config_from_object("django.conf:settings", namespace="CELERY")
# load all tasks
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
