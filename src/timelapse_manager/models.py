# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import uuid
from functools import partial

import datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import taggit.managers
from chainablemanager.manager import ChainableManager

from easy_thumbnails.fields import ThumbnailerImageField

from . import storage


class UUIDAuditedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    _created_at = models.DateTimeField(auto_now_add=True)
    _updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Camera(UUIDAuditedModel):
    name = models.CharField(blank=True, default='', max_length=255)
    notes = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class ImageManager(ChainableManager):
    class QuerySetMixin(object):
        pass

    def pick_closest(self, camera, shot_at, max_difference=None):
        """
        Picks closes available image. Raises DoesNotExists if no image is
        found within the range.
        This naïve implementation only looks forwards from the given shot_at
        datetime. A better version would also look into the past.
        """
        qs = self.filter(camera=camera, shot_at__gte=shot_at)
        if max_difference:
            qs = qs.filter(shot_at__lte=shot_at+max_difference)
        return qs.first()


@python_2_unicode_compatible
class Image(UUIDAuditedModel):
    sizes = ('640x480', '320x240', '160x120')
    camera = models.ForeignKey(Camera, related_name='images')
    shot_at = models.DateTimeField(null=True, blank=True, default=None)
    original = ThumbnailerImageField(null=True, blank=True, default='')
    scaled_at_160x120 = ThumbnailerImageField(
        null=True, blank=True, default='',
        upload_to=partial(storage.upload_to_thumbnail, size='160x120'))
    scaled_at_320x240 = ThumbnailerImageField(
        null=True, blank=True, default='',
        upload_to=partial(storage.upload_to_thumbnail, size='320x240'))
    scaled_at_640x480 = ThumbnailerImageField(
        null=True, blank=True, default='',
        upload_to=partial(storage.upload_to_thumbnail, size='640x480'))

    objects = ImageManager()

    def __str__(self):
        return self.original.name

    def create_thumbnails(self, force=False):
        from . import actions
        actions.create_thumbnails(self, force=force)
        self.save()


@python_2_unicode_compatible
class Annotation(UUIDAuditedModel):
    camera = models.ForeignKey(Camera, related_name='annotations')
    name = models.CharField(blank=True, default='', max_length=255)
    notes = models.TextField(blank=True, default='')
    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)
    tags = taggit.managers.TaggableManager()

    def images(self):
        return Image.objects.filter(
            camera=self.camera,
            shot_at__gte=self.start_at,
            shot_at__lte=self.end_at,
        )

    def __str__(self):
        return self.name


class DayManager(ChainableManager):
    class QuerySetMixin(object):
        def create_keyframe_thumbnails(self, force=False):
            for day in self:
                day.create_keyframe_thumbnails(force=force)

    def create_for_range(self, camera, start_on, end_on=None):
        if end_on is None:
            end_on = start_on
        current_day = start_on
        while current_day <= end_on:
            self.get_or_create(camera=camera, date=current_day)
            current_day = current_day + datetime.timedelta(days=1)


@python_2_unicode_compatible
class Day(UUIDAuditedModel):
    camera = models.ForeignKey(Camera, related_name='days')
    date = models.DateField()
    cover = models.ForeignKey(
        Image, null=True, blank=True, related_name='cover_for_days')
    key_frames = models.ManyToManyField(
        Image, blank=True, related_name='keyframe_for_days')

    objects = DayManager()

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return '{}'.format(self.date)

    def images(self):
        return Image.objects.filter(
            camera=self.camera,
            shot_at__date=self.date,
        )

    def image_count(self):
        return self.images().count()

    def set_key_frames(self):
        from . import actions
        actions.set_keyframes_for_image(self)

    def create_keyframe_thumbnails(self, force=False):
        print('creating thumbnails for {}'.format(self))
        if self.cover:
            self.cover.create_thumbnails(force=force)
        for key_frame in self.key_frames.all():
            key_frame.create_thumbnails(force=force)


