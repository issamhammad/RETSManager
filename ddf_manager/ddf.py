##This file is used by Celery for periodic updates

from __future__ import absolute_import, unicode_literals
from RETS_Manager.celery_app import ddf_app
from django.core.cache import cache
import time

LOCK_EXPIRE = 60* 60

@ddf_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    ##set update time in seconds here.
    sender.add_periodic_task(24*60*60 , update_ddf.s(), name="update_ddf")

@ddf_app.task
def update_ddf():
    from .manager import update_server
    acquire_lock = lambda: cache.add(1, "true", LOCK_EXPIRE)
    update_server(sample=True)
    release_lock = lambda: cache.delete(1)
