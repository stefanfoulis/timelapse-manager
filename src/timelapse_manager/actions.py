# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime

from django.core.files.storage import default_storage

from timelapse_manager.models import Image
from . import models, utils
import easy_thumbnails.files


def discover_images(storage=default_storage):
    """
    directory relative to default storage root
    """
    basedir = 'timelapse/overview'
    sizes = ('original', '640x480', '320x240', '160x120')
    camera = models.Camera.objects.all().first()
    for size in sizes:
        size_basedir = '/'.join([basedir, size])
        for daydir in storage.listdir(size_basedir)[0]:
            for imagename in storage.listdir('{}/{}'.format(size_basedir, daydir))[1]:
                if not imagename.lower().endswith('.jpg'):
                    continue
                shot_at = utils.datetime_from_filename(imagename)
                imagepath = '/'.join([size_basedir, daydir, imagename])
                defaults = {
                    'shot_at': shot_at,
                }
                if size == 'original':
                    defaults['original'] = imagepath
                else:
                    defaults['scaled_at_{}'.format(size)] = imagepath
                image, created = models.Image.objects.update_or_create(
                    camera=camera,
                    name=imagename,
                    defaults=defaults,
                )
                if created:
                    print('first size found {} {}'.format(size, imagename))
                else:
                    print('discovered. possibly new. {} {}'.format(size, imagename))



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
    day.cover = Image.objects.pick_closest(
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
        image = Image.objects.pick_closest(
            camera=day.camera,
            shot_at=datetime.datetime.combine(day.date, keyframe),
            max_difference=datetime.timedelta(hours=1)
        )
        if image:
            images.append(image)
    day.key_frames = images
