# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime

import collections
import os
from django.core.files import File
from yurl import URL

from timelapse_manager.storage import timelapse_storage
from . import models
from . import storage
from . import utils
import easy_thumbnails.files


def discover_images_on_day(
    camera,
    day_name,
    sizes=None,
    storage=storage.timelapse_storage,
    basedir='',
):
    sizes = sizes or ('original', '640x480', '320x240', '160x120')
    data = collections.defaultdict(dict)
    camera_basedir = os.path.join(basedir, camera.name)
    for size_name in storage.listdir(camera_basedir)[0]:
        if size_name not in sizes:
            continue
        size_basedir = os.path.join(camera_basedir, size_name)
        day_basedir = os.path.join(size_basedir, day_name)
        try:
            imagenames = storage.listdir(day_basedir)[1]
        except OSError:
            # the local filesystem storage fails when trying to list a directory
            # that does not exist. S3 storage just returns an empty list.
            # unfortunatly storage.exists() does not work on S3, as it returns
            # False for directories.
            continue
        for imagename in imagenames:
            if not imagename.lower().endswith('.jpg'):
                continue
            shot_at = utils.datetime_from_filename(imagename)
            imgdata = data[(camera.name, shot_at)]
            original_filename = utils.original_filename_from_filename(imagename)
            imagepath = os.path.join(day_basedir, imagename)

            imgdata['shot_at'] = shot_at
            imgdata['name'] = original_filename

            if size_name == 'original':
                imgdata['original'] = imagepath
            else:
                imgdata['scaled_at_{}'.format(size_name)] = imagepath
            print(' -> discovered {}'.format(imagepath))
    for imgdata in data.values():
        image, created = models.Image.objects.update_or_create(
            camera=camera,
            shot_at=imgdata.pop('shot_at'),
            defaults=imgdata,
        )
        if created:
            print(' ==> created {} {}'.format(size_name, imgdata['name']))
        else:
            print(' ==> updated {} {}'.format(size_name, imgdata['name']))


def discover_images(storage=storage.timelapse_storage, basedir='', limit_cameras=None, limit_days=None, sizes=None):
    """
    directory relative to default storage root
    """
    sizes = sizes or ('original', '640x480', '320x240', '160x120')
    for camera_name in storage.listdir(basedir)[0]:
        if limit_cameras and camera_name not in limit_cameras:
            continue
        try:
            camera = models.Camera.objects.get(name=camera_name)
        except models.Camera.DoesNotExist:
            continue
        camera_basedir = os.path.join(basedir, camera_name)
        days = set()
        for size_name in storage.listdir(camera_basedir)[0]:
            if size_name not in sizes:
                continue
            size_basedir = os.path.join(camera_basedir, size_name)
            try:
                day_names = storage.listdir(size_basedir)[0]
            except OSError:
                # the local filesystem storage fails when trying to list a
                # directory that does not exist. S3 storage just returns an
                # empty list. unfortunatly storage.exists() does not work on
                # S3, as it returns False for directories.
                day_names = []
            for day_name in day_names:
                if limit_days and not day_name in limit_days:
                    continue
                days.add(day_name)
        for day_name in days:
            discover_images_on_day(
                camera=camera,
                day_name=day_name,
                sizes=sizes,
                storage=storage,
                basedir=basedir,
            )


def normalize_image_url(url):
    """
    takes an s3 url or relative url and returns the part that is saved in the
    database (relative to the storage root).
    """
    if url.startswith('http://') or url.startswith('https://'):
        url = URL(url).path
        bucket = '/{}/'.format(timelapse_storage.bucket_name)
        if url.startswith(bucket):
            url = url[len(bucket):]
        if url.startswith(timelapse_storage.location):
            url = url[len(timelapse_storage.location):]
    if hasattr(timelapse_storage, 'base_url') and url.startswith(timelapse_storage.base_url):
        url = url[len(timelapse_storage.base_url):]
    if url.startswith('/'):
        url = url[1:]
    return url


def create_or_update_image_from_url(url):
    """
    takes an s3 url or relative url:
    - detects the size and other meta data
    - creates or updates the Image model with the new file
    """
    path = normalize_image_url(url)
    camera_name, size_name, day_name, filename = path.split('/')
    camera = models.Camera.objects.get(name=camera_name)
    shot_at = utils.datetime_from_filename(filename)

    defaults = dict(
        name=utils.original_filename_from_filename(filename),
    )

    if size_name == 'original':
        defaults['original'] = path
    else:
        defaults['scaled_at_{}'.format(size_name)] = path

    image, created = models.Image.objects.update_or_create(
        camera=camera,
        shot_at=shot_at,
        defaults=defaults,
    )
    if created:
        print(' ==> created {} {}'.format(size_name, filename))
    else:
        print(' ==> updated {} {}'.format(size_name, filename))
    return image, created


def create_thumbnail(image, size):
    if not image.original:
        return None  # raise instead?
    thumbnailer = easy_thumbnails.files.get_thumbnailer(image.original)
    size_tuple = tuple([int(sz) for sz in size.split('x')])
    options = {
        'size': size_tuple,
        'upscale': False,
    }
    thumb = thumbnailer.generate_thumbnail(options)
    content_file = thumb.file
    content_file.name = 'afile.jpg'
    setattr(image, 'scaled_at_{}'.format(size), content_file)


def create_thumbnails(image, force=False):
    for size in image.sizes:
        if force or not getattr(image, 'scaled_at_{}'.format(size)):
            print('  creating thumbnail {} {}'.format(image, size))
            create_thumbnail(image, size)
        else:
            print('  thumbnail already exists {} {}'.format(image, size))


def set_keyframes_for_day(day):
    day.cover = models.Image.objects.pick_closest(
        camera=day.camera,
        shot_at=datetime.datetime.combine(day.date, datetime.time(16, 0)),
        max_difference=datetime.timedelta(hours=2)
    )
    day.save()
    keyframes = [
        datetime.time(6, 0),
        datetime.time(9, 0),
        datetime.time(12, 30),
        datetime.time(15, 0),
        datetime.time(18, 0),
    ]
    images = []
    for keyframe in keyframes:
        image = models.Image.objects.pick_closest(
            camera=day.camera,
            shot_at=datetime.datetime.combine(day.date, keyframe),
            max_difference=datetime.timedelta(hours=1)
        )
        if image:
            images.append(image)
    day.key_frames = images


def image_count_by_type():
    qs = models.Image.objects.all()
    data = {
        '160x120': qs.exclude(scaled_at_160x120='').count(),
        '320x240': qs.exclude(scaled_at_320x240='').count(),
        '640x480': qs.exclude(scaled_at_640x480='').count(),
        'original': qs.exclude(original='').count(),
    }
    return '  '.join(['{}: {}'.format(key, value) for key, value in data.items()])


def render_movie(movie_rendering):
    from . import moviepy
    moviepath = moviepy.render_video(movie_rendering.movie.images())
    with open(moviepath, 'rb') as f:
        django_file = File(f)
        movie_rendering.file.save(os.path.basename(moviepath), django_file, save=True)
        movie_rendering.save()
