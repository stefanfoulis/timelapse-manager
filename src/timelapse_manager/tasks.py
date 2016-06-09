# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from celery.utils.log import get_task_logger
from celery import shared_task
from . import actions, models


logger = get_task_logger(__name__)


@shared_task
def discover_images(camera_id):
    logger.info('discover images for camera_id={}'.format(camera_id))
    camera = models.Camera.objects.get(id=camera_id)
    camera.discover_images()


@shared_task
def discover_images_on_day(
    day_id,
    set_keyframes=True,
    create_keyframe_thumbnails=True,
):
    logger.info('discover images on day day_id={}'.format(day_id))
    day = models.Day.objects.get(id=day_id)
    day.discover_images()
    if set_keyframes:
        day.set_key_frames()
    if create_keyframe_thumbnails:
        day.create_keyframe_thumbnails()


@shared_task
def set_keyframes_on_day(
    day_id,
    create_thumbnails=False,
):
    logger.info('create_keyframe_thumbnails_on_day day_id={}'.format(day_id))
    day = models.Day.objects.get(id=day_id)
    day.set_key_frames()
    if create_thumbnails:
        day.create_keyframe_thumbnails()


@shared_task
def create_keyframe_thumbnails_on_day(
    day_id,
):
    logger.info('create_keyframe_thumbnails_on_day day_id={}'.format(day_id))
    day = models.Day.objects.get(id=day_id)
    day.create_keyframe_thumbnails()


@shared_task
def render_movie(movie_rendering_id):
    logger.info('render_movie movie_rendering_id={}'.format(movie_rendering_id))
    movie_rendering = models.MovieRendering.objects.get(id=movie_rendering_id)
    movie_rendering.render()


@shared_task
def create_thumbnails_for_image(image_id, force=False):
    image = models.Image.objects.get(id=image_id)
    image.create_thumbnails(force=force)
