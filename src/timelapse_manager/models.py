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

        def with_faulty_scaled_filenames(self):
            return self.filter(
                Q(scaled_at_160x120__icontains='.original.') |
                Q(scaled_at_160x120__icontains='.JPG.') |
                Q(scaled_at_320x240__icontains='.original.') |
                Q(scaled_at_320x240__icontains='.JPG.') |
                Q(scaled_at_640x480__icontains='.original.') |
                Q(scaled_at_640x480__icontains='.JPG.')
            )

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
        return actions.create_or_update_image_from_url(url=url)

    def create_or_update_images_from_urls(self, urls):
        from . import actions
        return actions.create_or_update_images_from_urls(urls=urls)


@python_2_unicode_compatible
class Image(UUIDAuditedModel):
    sizes = (
        '640x480',
        '320x240',
        '160x120',
    )
    SIZE_CHOICES = [
        (size, size)
        for size in sizes
    ]
    camera = models.ForeignKey(Camera, related_name='images')
    name = models.CharField(
        max_length=255, blank=True, default='', db_index=True)
    shot_at = models.DateTimeField(
        null=True, blank=True, default=None, db_index=True)
    original = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255, db_index=True,
        storage=storage.timelapse_storage)
    original_md5 = models.CharField(
        max_length=32, blank=True, default='', db_index=True)
    scaled_at_160x120 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255, db_index=True,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='160x120'))
    scaled_at_160x120_md5 = models.CharField(
        max_length=32, blank=True, default='', db_index=True)
    scaled_at_320x240 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255, db_index=True,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='320x240'))
    scaled_at_320x240_md5 = models.CharField(
        max_length=32, blank=True, default='', db_index=True)
    scaled_at_640x480 = ThumbnailerImageField(
        null=True, blank=True, default='', max_length=255, db_index=True,
        storage=storage.timelapse_storage,
        upload_to=partial(storage.upload_to_thumbnail, size='640x480'))
    scaled_at_640x480_md5 = models.CharField(
        max_length=32, blank=True, default='', db_index=True)

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

    class Meta:
        ordering = (
            'start_at',
            'end_at',
        )

    def __str__(self):
        return self.name

    def images(self):
        if not (self.start_at and self.end_at):
            return Image.objects.empty()
        return Image.objects.filter(
            camera=self.camera,
            shot_at__gte=self.start_at,
            shot_at__lte=self.end_at,
        )

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

    def image_counts(self):
        return self.images().aggregate(
            original=models.Count('original', distinct=True),
            scaled_at_160x120=models.Count('scaled_at_160x120', distinct=True),
            scaled_at_320x240=models.Count('scaled_at_320x240', distinct=True),
            scaled_at_640x480=models.Count('scaled_at_640x480', distinct=True),
        )

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

    def sequence_union(self):
        # adapted from http://stackoverflow.com/a/15273749/245810
        ranges = self.tag_instances().values_list('start_at', 'end_at')
        union = []
        for begin, end in sorted(ranges):
            # TODO: make sure not using ">= begin-1" is ok
            if union and union[-1][1] >= begin:
                union[-1] = (min(union[-1][0], begin), max(union[-1][1], end))
            else:
                union.append((begin, end))
        return union

    def realtime_duration(self):
        duration = datetime.timedelta(0)
        for start_at, end_at in self.sequence_union():
            duration += end_at - start_at
        return duration

    def movie_duration(self):
        return self.realtime_duration() / self.speed_factor

    def images(self):
        union_ranges = self.sequence_union()
        qs = Image.objects.filter(
            camera=self.camera,
        )
        q = Q(name__isnull=True)  # it is always false
        for start_at, end_at in union_ranges:
            q = q | Q(
                shot_at__gte=start_at,
                shot_at__lte=end_at,
            )
        return qs.filter(q).distinct()

    def tag_images(self):
        # deprecated
        qs = Image.objects.filter(
            camera=self.camera,
        )
        q = Q(name__isnull=True)  # it is always false
        for tag in self.tag_instances():
            q = q | tag.get_q('shot_at')
        return qs.filter(q).distinct()

    def tags_display(self):
        return ', '.join(['{} ({} -> {})'.format(tag.name, tag.start_at, tag.end_at) for tag in self.tag_instances()])

    def image_count(self):
        return self.images().count()


@python_2_unicode_compatible
class MovieRendering(UUIDAuditedModel):
    movie = models.ForeignKey(Movie, related_name='renderings')
    size = models.CharField(
        max_length=32, choices=[(imgsize, imgsize) for imgsize in Image.sizes],
        default='160x120',
    )
    fps = models.FloatField(default=15.0)
    format = models.CharField(default='mp4', max_length=255)
    file = models.FileField(
        null=True, blank=True, default='', max_length=255, db_index=True,
        storage=storage.timelapse_storage,
        upload_to=storage.upload_to_movie_rendering,
    )
    file_md5 = models.CharField(
        max_length=32, blank=True, default='', db_index=True)

    def __str__(self):
        return "{}: {} {}fps".format(self.movie, self.format, self.fps)

    def expected_frame_count(self):
        movie_duration = self.movie.movie_duration()
        fps = self.fps
        return movie_duration.total_seconds() * fps

    def wanted_frame_timestamps(self):
        for start_at, end_at in self.movie.sequence_union():
            realtime_duration = (end_at - start_at).total_seconds()
            target_duration = realtime_duration / self.movie.speed_factor
            wanted_image_count = target_duration * self.fps
            wanted_image_every_realtime_seconds = realtime_duration / wanted_image_count
            current_timestamp = start_at
            while current_timestamp <= end_at:
                yield current_timestamp
                current_timestamp += datetime.timedelta(
                    seconds=wanted_image_every_realtime_seconds)

    def create_frames(self):
        from . import actions
        return actions.create_frames_for_movie_rendering(movie_rendering=self)

    def render(self):
        from . import actions
        return actions.render_movie(movie_rendering=self)


class Frame(UUIDAuditedModel):
    movie_rendering = models.ForeignKey(MovieRendering, related_name='frames')
    number = models.PositiveIntegerField()
    realtime_timestamp = models.DateTimeField()
    image = models.ForeignKey(
        Image, related_name='frames', null=True, blank=True)

    class Meta:
        ordering = (
            'movie_rendering',
            'number',
        )

    def pick_image(self):
        self.image = Image.objects.pick_closest(
            camera=self.movie_rendering.movie.camera,
            shot_at=self.realtime_timestamp,
            max_difference=datetime.timedelta(hours=1)
        )
