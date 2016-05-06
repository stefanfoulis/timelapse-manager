from celery import shared_task
from . import actions, models


@shared_task
def discover_images(camera_id):
    camera = models.Camera.objects.get(id=camera_id)
    camera.discover_images()


@shared_task
def discover_images_on_day(
    day_id,
    set_keyframes=True,
    create_keyframe_thumbnails=True,
):
    day = models.Day.objects.get(id=day_id)
    day.discover_images()
    if set_keyframes:
        day.set_key_frames()
    if create_keyframe_thumbnails:
        day.create_keyframe_thumbnails()


@shared_task
def create_keyframe_thumbnails_on_day(
    day_id,
    create_thumbnails=False,
):
    day = models.Day.objects.get(id=day_id)
    day.create_keyframe_thumbnails()
    if create_thumbnails:
        day.create_keyframe_thumbnails()


@shared_task
def render_movie(movie_rendering_id):
    movie_rendering = models.MovieRendering.objects.get(id=movie_rendering_id)
    movie_rendering.render()
