from celery import shared_task
from . import actions


@shared_task
def discover_images():
    actions.discover_images()
