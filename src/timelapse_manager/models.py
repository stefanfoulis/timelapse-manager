# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import uuid
from functools import partial

import datetime
from django.db import models
from django.db.models import Q
from django.utils.encoding import python_2_unicode_compatible

from chainablemanager.manager import ChainableManager
from easy_thumbnails.fields import ThumbnailerImageField

from . import storage
import djcelery


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

    def create_days(self):
        created_days = []
        for date in self.images.all().dates('shot_at', 'day'):
            day, created = Day.objects.get_or_create(
                camera=self,
                date=date,
            )
            if created:
                created_days.append(day)
        return created_days

    def discover_images(self):
        from . import actions
        actions.discover_images(limit_cameras=[self])


class ImageManager(ChainableManager):
    class QuerySetMixin(object):
        def with_missing_thumbnails(self, camera=None):
            qs = self.filter(original__isnull=False)
            if camera:
                qs = qs.filter(camera=camera)
            qs = qs.filter((
                Q(scaled_at_160x120='') |
                Q(scaled_at_320x240='') |
                Q(scaled_at_640x480='')
            ))
            return qs

        def create_missing_thumbnails(self, camera=None):
            for img in self.with_missing_thumbnails(camera=camera).iterator():
                img.create_thumbnails()

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

    def create_or_update_from_url(self, url):
        from . import actions
        return actions.create_or_update_image_from_url(url)



@python_2_unicode_compatible
class Image(UUIDAuditedModel):
    sizes = (
        '640x480',
        '320x240',
        '160x120',
    )
    camera = models.ForeignKey(Camera, related_name='images')
    name = models.CharField(max_length=255, blank=True, default='')
    shot_at = models.DateTimeField(
        null=True, blank=True, default=None, db_index=True)
    original = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255,
        storage=storage.timelapse_storage)
    scaled_at_160x120 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='160x120'))
    scaled_at_320x240 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='320x240'))
    scaled_at_640x480 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='640x480'))

    objects = ImageManager()

    class Meta:
        unique_together = (
            ('camera', 'shot_at',),
        )
        ordering = ('shot_at',)

    def __str__(self):
        return self.original.name

    def create_thumbnails(self, force=False):
        from . import actions
        actions.create_thumbnails(self, force=force)
        self.save()

    def tags(self):
        return Tag.objects.filter(
            camera=self.camera,
            start_at__lte=self.shot_at,
            end_at__gte=self.shot_at,
        )

    def get_file_for_size(self, size):
        if size == 'original':
            return self.original or None
        assert size in ['160x120', '320x240', '640x480']
        if not getattr(self, 'scaled_at_{}'.format(size)):
            if self.original:
                self.create_thumbnails()
            else:
                return None
        return getattr(self, 'scaled_at_{}'.format(size))


@python_2_unicode_compatible
class Tag(UUIDAuditedModel):
    camera = models.ForeignKey(Camera, related_name='tags')
    name = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    def images(self):
        if not (self.start_at and self.end_at):
            return Image.objects.empty()
        return Image.objects.filter(
            camera=self.camera,
            shot_at__gte=self.start_at,
            shot_at__lte=self.end_at,
        )

    def __str__(self):
        return self.name

    def tag_info(self):
        return TagInfo.objects.get_or_create(name=self.name)[0]

    def save(self, *args, **kwargs):
        r = super(Tag, self).save(*args, **kwargs)
        TagInfo.objects.get_or_create(name=self.name)
        return r

    def duration(self):
        if not (self.start_at and self.end_at):
            return None
        return self.end_at - self.start_at

    def image_count(self):
        return self.images().count()

    def get_q(self, fieldname):
        return Q(**{
            '{}__gte'.format(fieldname): self.start_at,
            '{}__lte'.format(fieldname): self.end_at,
        })


@python_2_unicode_compatible
class TagInfo(UUIDAuditedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

    def tags(self):
        return Tag.objects.filter(name=self.name)


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
    date = models.DateField(db_index=True)
    cover = models.ForeignKey(
        Image, null=True, blank=True, related_name='cover_for_days')
    key_frames = models.ManyToManyField(
        Image, blank=True, related_name='keyframe_for_days')

    objects = DayManager()

    class Meta:
        ordering = ('date',)
        unique_together = ('camera', 'date')

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
        actions.set_keyframes_for_day(self)

    def create_keyframe_thumbnails(self, force=False):
        print('creating thumbnails for {}'.format(self))
        if self.cover:
            self.cover.create_thumbnails(force=force)
        for key_frame in self.key_frames.all():
            key_frame.create_thumbnails(force=force)

    def discover_images(self):
        from . import actions
        actions.discover_images_on_day(
            camera=self.camera,
            day_name=str(self.date),
        )


@python_2_unicode_compatible
class Movie(UUIDAuditedModel):
    camera = models.ForeignKey(Camera, related_name='movies')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default=None)

    speed_factor = models.FloatField(default=4000.0)
    tags = models.ManyToManyField(TagInfo, related_name='movies', blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def tag_instances(self):
        tag_names = self.tags.values_list('name', flat=True)
        return Tag.objects.filter(name__in=tag_names)

    def images(self):
        qs = Image.objects.filter(
            camera=self.camera,
        )
        q = Q(name__isnull=True)  # it is always false
        for tag in self.tag_instances():
            q = q | tag.get_q('shot_at')
        qs = qs.filter(q)
        return qs.distinct()

    def tags_display(self):
        return ', '.join(['{} ({} -> {})'.format(tag.name, tag.start_at, tag.end_at) for tag in self.tag_instances()])

    def image_count(self):
        return self.images().count()


@python_2_unicode_compatible
class MovieRendering(UUIDAuditedModel):
    movie = models.ForeignKey(Movie, related_name='renderings')
    fps = models.FloatField(default=15.0)
    format = models.CharField(default='mp4', max_length=255)
    file = models.FileField(blank=True, default='', max_length=255)

    def __str__(self):
        return "{}: {} {}fps".format(self.movie, self.format, self.fps)

    def render(self):
        from . import actions
        actions.render_movie(movie_rendering=self)
