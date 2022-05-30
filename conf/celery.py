from __future__ import absolute_import
from celery import Celery
from django.conf import settings
import os
from logging import getLogger


logger = getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
app = Celery("conf")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_tasks(self):
    logger.debug(f"Request: {self.request!r}")
