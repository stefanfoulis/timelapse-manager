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
    original_basedir = 'timelapse/overview/original'
    thumbsizes = ('640x480', '320x240', '160x120')
    camera = models.Camera.objects.all().first()
    for daydir in storage.listdir(original_basedir)[0]:
        for imagename in storage.listdir('{}/{}'.format(original_basedir, daydir))[1]:
            if not imagename.lower().endswith('.jpg'):
                continue
            print('discovered {} {}'.format(daydir, imagename))
            shot_at = utils.datetime_from_filename(imagename)
            imagepath = '/'.join([original_basedir, daydir, imagename])
            defaults = {'shot_at': shot_at}
            for thumbsize in thumbsizes:
                thumbpath = 'timelapse/overview/{}/{}/{}'.format(
                    thumbsize, daydir, imagename)
                if storage.exists(thumbpath):
                    defaults['scaled_at_{}'.format(thumbsize)] = thumbpath
            image = models.Image.objects.update_or_create(
                camera=camera,
                original=imagepath,
                defaults=defaults,
            )


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
    # import types
    # from django.db.models.fields.files import FieldFile
    #
    # def save(*args, **kwargs):
    #     FieldFile.save(*args, **kwargs)
    # thumb.save = types.MethodType(save, thumb)
    content_file = thumb.file
    content_file.name = 'afile.jpg'
    setattr(image, 'scaled_at_{}'.format(size), content_file)


def create_thumbnails(image, force=False):
    for size in image.sizes:
        if force or not getattr(image, 'scaled_at_{}'.format(size)):
            create_thumbnail(image, size)
        else:
            print('  skipping {} {}'.format(image, size))


def set_keyframes_for_image(image):
    image.cover = Image.objects.pick_closest(
        camera=image.camera,
        shot_at=datetime.datetime.combine(self.date, datetime.time(16, 0)),
        max_difference=datetime.timedelta(hours=2)
    )
    image.save()
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
            camera=image.camera,
            shot_at=datetime.datetime.combine(self.date, keyframe),
            max_difference=datetime.timedelta(hours=1)
        )
        if image:
            images.append(image)
    image.key_frames = images
