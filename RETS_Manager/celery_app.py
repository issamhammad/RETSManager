from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RETS_Manager.settings')

ddf_app = Celery('ddf', backend='redis://redis:6379/1',broker='redis://redis:6379/1')

ddf_app.autodiscover_tasks(['ddf'])

