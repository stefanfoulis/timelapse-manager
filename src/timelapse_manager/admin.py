# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import smart_text

from .models import Camera, Image, Day, Tag, TagInfo, Movie, MovieRendering, \
    Frame
from . import tasks, utils


class CameraAdmin(admin.ModelAdmin):
    actions = (
        'create_days_for_existing_images_action',
        'create_days_for_oldest_existing_image_until_today_action',
    )

    def create_days_for_existing_images_action(self, request, queryset):
        for camera in queryset:
            days = camera.create_days()
            self.message_user(
                request,
                '{}: created {} days. Now has a total of {} days.'.format(
                    camera,
                    len(days),
                    camera.days.all().count(),
                )
            )

    def create_days_for_oldest_existing_image_until_today_action(self, request, queryset):
        for camera in queryset:
            day_one = camera.images.order_by('shot_at').first()
            if not day_one:
                self.message_user(
                    request,
                    '{}: no existing images!',
                    level=messages.WARNING,
                )
                continue
            days = []
            start_on = day_one.shot_at.date()
            end_on = datetime.date.today()
            for date in utils.daterange(
                start_on=start_on,
                end_on=end_on,
            ):
                day, created = Day.objects.get_or_create(
                    camera=camera,
                    date=date,
                )
                if created:
                    days.append(day)
            self.message_user(
                request,
                '{}: created {} days. Now has a total of {} days. ({} - {})'.format(
                    camera,
                    len(days),
                    camera.days.all().count(),
                    start_on,
                    end_on,
                )
            )

    def discover_images_action(self, request, queryset):
        for camera in queryset:
            tasks.discover_images.delay(camera_id=camera.id)


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'camera',
        'shot_at',
        'original',
        'scaled_at_640x480',
        'scaled_at_320x240',
        'scaled_at_160x120',
    )
    list_filter = (
        'camera',
        # TODO: filter by has original, has scaled
    )
    date_hierarchy = 'shot_at'
    search_fields = (
        'original',
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
    )
    actions = (
        'create_thumbnails_action',
    )

    def create_thumbnails_action(self, request, queryset):
        for obj in queryset:
            tasks.create_thumbnails_for_image.delay(image_id=str(obj.id))


class DayAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'cover_img',
        'keyframes_img',
        'image_counts_html',
    )
    actions = (
        'set_keyframes_action',
        'create_keyframe_thumbnails_action',
        'set_keyframes_and_create_keyframe_thumbnails_action',
        'discover_images_action',
        'discover_images_and_process_action',
    )
    raw_id_fields = (
        'cover',
    )
    fields = (
        'camera',
        'date',
        'cover',
    )
    ordering = (
        '-date',
    )
    date_hierarchy = 'date'

    def get_queryset(self, request):
        qs = (
            super(DayAdmin, self).get_queryset(request)
            .select_related('cover')
            .prefetch_related('key_frames')
        )
        return qs

    def set_keyframes_action(self, request, queryset):
        for day in queryset:
            day.set_key_frames()

    def create_keyframe_thumbnails_action(self, request, queryset):
        for day in queryset:
            tasks.create_keyframe_thumbnails_on_day.delay(
                day_id=smart_text(day.id))

    def set_keyframes_and_create_keyframe_thumbnails_action(
            self, request, queryset):
        for day in queryset:
            tasks.set_keyframes_on_day.delay(
                day_id=smart_text(day.id),
                create_thumbnails=True,
            )

    def discover_images_action(self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(
                day_id=smart_text(day.id))

    def discover_images_and_process_action(
            self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(
                day_id=smart_text(day.id),
                set_keyframes=True,
                create_keyframe_thumbnails=True,
            )

    def cover_img(self, obj):
        image = obj.cover
        if not image:
            return ''
        if image.scaled_at_160x120:
            img_html = '<img src="{img_src}" style="width: 160px; height: 120px" />'.format(
                img_src=image.scaled_at_160x120.url,
            )
        else:
            img_html = '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
        if image.original:
            img_html = '<a href="{link}">{img_html}</a>'.format(
                link=image.original.url,
                img_html=img_html,
            )
        return img_html
    cover_img.allow_tags = True

    def keyframes_img(self, obj):
        html_list = []
        for image in obj.key_frames.all().order_by('shot_at'):
            if image.scaled_at_160x120:
                html = '<img src="{}" style="width: 160px; height: 120px" />'.format(
                    image.scaled_at_160x120.url)
            else:
                html = '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
            if image.original:
                html = '<a href="{link}">{img_html}</a>'.format(
                    link=image.original.url,
                    img_html=html,
                )
            html_list.append(html)
        return "&nbsp;".join(html_list)
    keyframes_img.allow_tags = True

    def image_counts_html(self, obj):
        return '<br/>'.join([
            '<em>{}</em>: {}'.format(key, value)
            for key, value in sorted(obj.image_counts().items())
        ])
    image_counts_html.allow_tags = True
    image_counts_html.short_description = 'image counts'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_at',
        'end_at',
        'duration',
        'image_count',
    )
    readonly_fields = (
        'image_count',
        'duration',
    )


class TagInfoAdmin(admin.ModelAdmin):
    pass


class MovieRenderingInline(admin.TabularInline):
    model = MovieRendering
    extra = 0
    readonly_fields = (
        'frame_count',
        'expected_frame_count',
        'admin_link',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(frame_count=models.Count('frames'))

    def frame_count(self, obj):
        return obj.frame_count

    def admin_link(self, obj):
        return '<a target="_blank" href="{}">edit</a>'.format(
            reverse('admin:timelapse_manager_movierendering_change', args=('{}'.format(obj.pk),))
        )
    admin_link.allow_tags = True
    admin_link.short_description = ''


class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tags_display',
        'image_count',
    )
    readonly_fields = (
        'tags_html',
        'sequence_union_html',
        'realtime_duration',
        'movie_duration',
        'image_count',
    )
    inlines = (
        MovieRenderingInline,
    )
    filter_horizontal = (
        'tags',
    )

    def tags_html(self, obj):
        return '<br/>'.join([
            '{} -> {} {}'.format(tag.start_at, tag.end_at, tag.name)
            for tag in obj.tag_instances()
        ])
    tags_html.allow_tags = True
    tags_html.short_description = 'Tags'

    def sequence_union_html(self, obj):
        return '<br/>'.join([
            '{} -> {}'.format(start_at, end_at)
            for start_at, end_at in obj.sequence_union()
        ])
    sequence_union_html.allow_tags = True
    sequence_union_html.short_description = 'Union'


class MovieRenderingAdmin(admin.ModelAdmin):
    actions = (
        'create_frames_action',
        'render_action',
    )
    list_display = (
        '__str__',
        'size',
        'frame_count',
        'expected_frame_count',
    )
    readonly_fields = (
        'expected_frame_count',
        'wanted_frame_timestamps_html',
        'preview_html',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(frame_count=models.Count('frames'))

    def frame_count(self, obj):
        return obj.frame_count

    def wanted_frame_timestamps_html(self, obj):
        timestamps = list(obj.wanted_frame_timestamps())
        html_title = '<strong>{}</strong> frames<br/>'.format(len(timestamps))
        html_ts = '<br/>'.join([
            '{}'.format(timestamp)
            for timestamp in obj.wanted_frame_timestamps()
        ])
        return html_title + html_ts
    wanted_frame_timestamps_html.allow_tags = True
    wanted_frame_timestamps_html.short_description = 'wanted frame timestamps'

    def preview_html(self, obj):
        return '''<img src="{}" />'''.format(obj.file.url)
    preview_html.allow_tags = True

    def create_frames_action(self, request, queryset):
        for obj in queryset:
            obj.create_frames()

    def render_action(self, request, queryset):
        for obj in queryset:
            tasks.render_movie.delay(
                movie_rendering_id='{}'.format(obj.id)
            )


class FrameAdmin(admin.ModelAdmin):
    list_filter = (
        'movie_rendering',
    )
    list_display = (
        'preview_html',
        'movie_rendering',
        'number',
        'realtime_timestamp',
    )
    actions = (
        'create_thumbnails_action',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('image')

    def preview_html(self, obj):
        if obj.image.scaled_at_160x120:
            return '<img src="{}" />'.format(obj.image.scaled_at_160x120.url)
        else:
            return '<div style="width: 160px; height: 120px; border: 1px solid gray;"></div>'
    preview_html.allow_tags = True

    def create_thumbnails_action(self, request, queryset):
        for obj in queryset:
            tasks.create_thumbnails_for_image.delay(image_id=str(obj.image_id))


admin.site.register(Camera, CameraAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagInfo, TagInfoAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieRendering, MovieRenderingAdmin)
admin.site.register(Frame, FrameAdmin)
